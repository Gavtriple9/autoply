#!/usr/bin/env python3

import asyncio
import json
from collections import OrderedDict
from playwright.async_api import async_playwright, Page, ElementHandle

URL = "https://www.publix.com/savings/weekly-ad/bogo"

CARD_SELECTOR = '[data-qa="savings-weekly-card"]'
HEADING_SELECTOR = 'h2[id$="-heading"]'


async def get_category_for_card(page: Page, card: ElementHandle) -> str | None:
    return await page.evaluate(
        """([card, selector]) => {
            const cardY = card.getBoundingClientRect().top + window.scrollY;

            const headings = Array.from(
                document.querySelectorAll(selector)
            );

            let category = null;

            for (const h of headings) {
                const y = h.getBoundingClientRect().top + window.scrollY;
                if (y <= cardY) {
                    category = h.innerText.trim();
                } else {
                    break;
                }
            }

            return category;
        }""",
        [card, HEADING_SELECTOR],
    )


async def get_card_metrics(page: Page) -> dict:
    await page.wait_for_selector(CARD_SELECTOR)

    return await page.evaluate(
        """(selector) => {
            const el = document.querySelector(selector);
            if (!el) return null;

            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);

            const cardHeight =
                rect.height +
                parseFloat(style.marginTop) +
                parseFloat(style.marginBottom);

            const firstCardY = rect.top + window.scrollY;

            return {
                cardHeight,
                firstCardY
            };
        }""",
        CARD_SELECTOR,
    )


async def extract_title_text(card: ElementHandle) -> str | None:
    title_el = await card.query_selector('[data-qa-automation="prod-title"]')
    if title_el:
        return (await title_el.inner_text()).strip()
    return None


async def extract_savings_text(card: ElementHandle) -> str | None:
    savings_el = await card.query_selector("span.additional-info")
    if savings_el:
        return (await savings_el.inner_text()).strip()
    return None


async def extract_offer_text(card: ElementHandle) -> str | None:
    offer_el = await card.query_selector(".p-savings-badge__text span")
    if offer_el:
        return (await offer_el.inner_text()).strip()
    return None


async def add_new_deals(master_list: list, new_deals: list):
    existing_titles = {deal["title"] for deal in master_list}
    for deal in new_deals:
        if deal["title"] not in existing_titles:
            master_list.append(deal)


def group_deals_by_category(deals: list[dict]) -> list[dict]:
    grouped = OrderedDict()

    for deal in deals:
        category = deal.get("category") or "Uncategorized"

        if category not in grouped:
            grouped[category] = []

        item = {
            "title": deal["title"],
            "savings": deal["savings"],
            "offer": deal["offer"],
        }

        grouped[category].append(item)

    return [
        {
            "category": category,
            "items": items,
        }
        for category, items in grouped.items()
    ]


async def scrape_publix(page: Page, pause: float = 1.0) -> list:
    last_scroll_y = -1
    deals = []

    metrics = await get_card_metrics(page)

    card_height = metrics["cardHeight"]
    first_card_y = metrics["firstCardY"]

    if not card_height:
        raise RuntimeError("Could not determine card height")

    await page.evaluate("(y) => window.scrollTo(0, y)", first_card_y)
    last_scroll_y = -1

    clean_deals = []

    while True:
        scroll_y = await page.evaluate("() => window.scrollY")

        # Stop if scrolling no longer advances
        if scroll_y == last_scroll_y:
            print("No further scroll possible")
            break

        deals = await scrape_viewport(page)
        await add_new_deals(clean_deals, deals)

        # Scroll exactly one card down
        await page.evaluate("(y) => window.scrollTo(0, y)", scroll_y + card_height)

        last_scroll_y = scroll_y

    return clean_deals


async def scrape_viewport(page: Page) -> list:
    cards = await page.query_selector_all(CARD_SELECTOR)
    deals = []

    for card in cards:
        # Only cards currently in viewport
        visible = await page.evaluate(
            """el => {
                const r = el.getBoundingClientRect();
                return r.bottom > 0 && r.top < window.innerHeight;
            }""",
            card,
        )

        if not visible:
            continue

        title = await extract_title_text(card)
        if not title:
            continue

        category = await get_category_for_card(page, card)
        savings = await extract_savings_text(card)
        offer = await extract_offer_text(card)

        deal = {
            "category": category,
            "title": title,
            "savings": savings,
            "offer": offer,
        }

        deals.append(deal)

    return deals


async def async_main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page(
            color_scheme="dark", viewport={"width": 1280, "height": 1600}
        )

        await page.goto(URL, wait_until="domcontentloaded")

        # Wait for the content wrapper to be present
        await page.wait_for_selector(".weekly-ad-xp-content-wrapper", timeout=15000)
        await asyncio.sleep(10)
        print("Page loaded")

        deals = await scrape_publix(page, pause=0.0)
        print(f"Total deals found: {len(deals)}")
        await browser.close()

    with open("publix.json", "w") as f:
        json.dump(deals, f, indent=2)

    print(f"Scraped {len(deals)} deals\n")

    for deal in deals[:5]:
        print(deal)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
