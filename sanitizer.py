#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class RepairResult:
    data: Any
    repaired: bool
    note: str | None = None


_WS_RE = re.compile(r"\s+")


def _norm_ws(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _norm_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    u = unit.strip().lower()
    if u in {"lb", "lbs", "pound", "pounds"}:
        return "lb"
    if u in {"ea", "each"}:
        return "each"
    return u


def parse_savings(savings: str | None) -> dict[str, Any] | None:
    if savings is None:
        return None

    s = _norm_ws(savings)
    if not s:
        return None

    low = s.lower()
    if low in {"your choice", "surprisingly low price"}:
        return {"kind": "text", "text": s}

    # Examples:
    # - Save Up To $5.55 Lb
    # - Save Up To $11.29
    # - Save $1.00
    m = re.match(
        r"^save\s+up\s+to\s*\$?\s*(\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$",
        s,
        flags=re.I,
    )
    if m:
        amount = _safe_float(m.group(1))
        unit = _norm_unit(m.group(2))
        if amount is None:
            return {"kind": "text", "text": s}
        return {
            "kind": "save_up_to",
            "amount": amount,
            "unit": unit,
            "currency": "USD",
        }

    m = re.match(
        r"^save\s*\$?\s*(\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$",
        s,
        flags=re.I,
    )
    if m:
        amount = _safe_float(m.group(1))
        unit = _norm_unit(m.group(2))
        if amount is None:
            return {"kind": "text", "text": s}
        return {
            "kind": "save",
            "amount": amount,
            "unit": unit,
            "currency": "USD",
        }

    return {"kind": "text", "text": s}


def parse_offer(offer: str | None) -> dict[str, Any] | None:
    if offer is None:
        return None

    s = _norm_ws(offer)
    if not s:
        return None

    low = s.lower()

    # Buy 1 Get 1 Free
    m = re.match(r"^buy\s+(\d+)\s+get\s+(\d+)\s+free$", s, flags=re.I)
    if m:
        return {
            "kind": "bogo",
            "buy_qty": int(m.group(1)),
            "get_qty": int(m.group(2)),
            "free": True,
        }

    # 2 for $10.00
    m = re.match(r"^(\d+)\s+for\s+\$?\s*(\d+(?:\.\d+)?)\s*$", s, flags=re.I)
    if m:
        qty = int(m.group(1))
        total = _safe_float(m.group(2))
        if total is None or qty <= 0:
            return {"kind": "text", "text": s}
        return {
            "kind": "multibuy",
            "qty": qty,
            "total_price": total,
            "unit_price": round(total / qty, 4),
            "currency": "USD",
        }

    # 10/$10.00
    m = re.match(r"^(\d+)\s*/\s*\$?\s*(\d+(?:\.\d+)?)\s*$", s, flags=re.I)
    if m:
        qty = int(m.group(1))
        total = _safe_float(m.group(2))
        if total is None or qty <= 0:
            return {"kind": "text", "text": s}
        return {
            "kind": "multibuy",
            "qty": qty,
            "total_price": total,
            "unit_price": round(total / qty, 4),
            "currency": "USD",
        }

    # $3.00 off WITH MFR DIGITAL COUPON
    m = re.match(
        r"^\$?\s*(\d+(?:\.\d+)?)\s*off\s+with\s+mfr\s+digital\s+coupon\s*$",
        s,
        flags=re.I,
    )
    if m:
        amount_off = _safe_float(m.group(1))
        if amount_off is None:
            return {"kind": "text", "text": s}
        return {
            "kind": "coupon",
            "amount_off": amount_off,
            "currency": "USD",
            "scope": "mfr_digital_coupon",
        }

    # Sale Price $29.99
    m = re.match(r"^sale\s+price\s+\$?\s*(\d+(?:\.\d+)?)\s*$", s, flags=re.I)
    if m:
        amount = _safe_float(m.group(1))
        if amount is None:
            return {"kind": "text", "text": s}
        return {"kind": "price", "amount": amount, "unit": None, "currency": "USD"}

    # $8.99 lb / $9.99 each / $3.99
    m = re.match(
        r"^\$\s*(\d+(?:\.\d+)?)\s*(lb|lbs|each|ea)?\s*$",
        s,
        flags=re.I,
    )
    if m:
        amount = _safe_float(m.group(1))
        unit = _norm_unit(m.group(2))
        if amount is None:
            return {"kind": "text", "text": s}
        return {"kind": "price", "amount": amount, "unit": unit, "currency": "USD"}

    # Surprisingly Low Price
    if low == "surprisingly low price":
        return {"kind": "text", "text": s}

    return {"kind": "text", "text": s}


def _iter_items(data: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for cat in data.get("deals", []) or []:
        category = cat.get("category") or "Uncategorized"
        for item in cat.get("items", []) or []:
            if isinstance(item, dict):
                yield category, item


def sanitize_publix_payload(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    warnings: list[str] = []

    ts = data.get("timestamp")
    if isinstance(ts, str):
        try:
            # Publix scraper writes ISO-8601 with offset
            datetime.fromisoformat(ts)
        except ValueError:
            warnings.append("timestamp is not ISO-8601")
    elif ts is not None:
        warnings.append("timestamp is not a string")

    offer_kind_counts: Counter[str] = Counter()
    savings_kind_counts: Counter[str] = Counter()

    # Work in-place on a deep-ish copy that preserves unknown fields.
    out = json.loads(json.dumps(data))

    for category, item in _iter_items(out):
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            warnings.append(f"missing/invalid title in category '{category}'")

        savings_raw = item.get("savings")
        offer_raw = item.get("offer")

        savings_parsed = parse_savings(
            savings_raw if isinstance(savings_raw, str) else None
        )
        offer_parsed = parse_offer(offer_raw if isinstance(offer_raw, str) else None)

        if savings_parsed is not None:
            savings_kind_counts[savings_parsed.get("kind", "unknown")] += 1
        else:
            savings_kind_counts["null"] += 1

        if offer_parsed is not None:
            offer_kind_counts[offer_parsed.get("kind", "unknown")] += 1
        else:
            offer_kind_counts["null"] += 1

        item["savings_raw"] = savings_raw
        item["offer_raw"] = offer_raw
        item["savings_parsed"] = savings_parsed
        item["offer_parsed"] = offer_parsed

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": len(out.get("deals", []) or []),
        "items": sum(1 for _ in _iter_items(out)),
        "savings_kind_counts": dict(savings_kind_counts),
        "offer_kind_counts": dict(offer_kind_counts),
        "warnings": warnings,
    }

    out["meta"] = meta
    return out, meta


def _try_load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _repair_truncated_json(text: str) -> str | None:
    """Best-effort repair for JSON truncated at EOF.

    This is intentionally conservative: it only attempts to repair when we can
    balance brackets/braces outside of strings, and it appends the missing
    closers. It won't fix arbitrary corruption.
    """

    s = text.lstrip("\ufeff")

    stack: list[str] = []
    in_string = False
    escape = False

    for ch in s:
        if in_string:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in {"}", "]"}:
            if stack and stack[-1] == ch:
                stack.pop()
            else:
                return None

    if in_string:
        return None

    if not stack:
        return None

    repaired = s.rstrip()

    # Remove a dangling trailing comma if present.
    repaired = re.sub(r",\s*$", "", repaired)

    # If we end with ':' we can't safely repair.
    if re.search(r":\s*$", repaired):
        return None

    return repaired + "".join(reversed(stack))


def load_json_maybe_repair(path: Path) -> RepairResult:
    try:
        return RepairResult(data=_try_load_json(path), repaired=False)
    except json.JSONDecodeError as e:
        # Only attempt repair when it looks like an EOF truncation.
        msg = str(e).lower()
        text = path.read_text(encoding="utf-8", errors="replace")

        if "unterminated" in msg or "expecting" in msg:
            repaired_text = _repair_truncated_json(text)
            if repaired_text:
                try:
                    return RepairResult(
                        data=json.loads(repaired_text),
                        repaired=True,
                        note="input JSON looked truncated; repaired by appending missing brackets/braces",
                    )
                except json.JSONDecodeError:
                    pass

        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sanitize Publix weekly-ad JSON: parse savings/offers, normalize unicode, and emit a report.",
    )
    parser.add_argument("input", type=Path, help="Path to publix.json")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path for sanitized JSON (default: <input>.sanitized.json)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Output path for report JSON (default: <input>.report.json)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON outputs",
    )

    args = parser.parse_args(argv)

    in_path: Path = args.input
    out_path: Path = args.out or in_path.with_suffix(in_path.suffix + ".sanitized.json")
    report_path: Path = args.report or in_path.with_suffix(
        in_path.suffix + ".report.json"
    )

    try:
        loaded = load_json_maybe_repair(in_path)
    except FileNotFoundError:
        print(f"error: file not found: {in_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: failed to parse JSON: {in_path}: {e}", file=sys.stderr)
        return 2

    if not isinstance(loaded.data, dict):
        print("error: expected top-level JSON object", file=sys.stderr)
        return 2

    sanitized, report = sanitize_publix_payload(loaded.data)

    indent = 2 if args.pretty else None

    out_path.write_text(
        json.dumps(sanitized, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
    )
    report_payload = {
        **report,
        "input": str(in_path),
        "output": str(out_path),
        "repaired": loaded.repaired,
        "repair_note": loaded.note,
    }
    report_path.write_text(
        json.dumps(report_payload, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "ok": True,
                "repaired": loaded.repaired,
                "output": str(out_path),
                "report": str(report_path),
                "categories": report.get("categories"),
                "items": report.get("items"),
                "warnings": len(report.get("warnings", [])),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
