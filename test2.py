from __future__ import annotations

from openai import NotFoundError, OpenAI

BASE_URL = "http://localhost:5000/v1"
MODEL = "local-model"
FILE_PATH = "publix.json"

client = OpenAI(base_url=BASE_URL, api_key="not-needed")


def read_text_file(path: str, *, max_chars: int = 40_000) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(max_chars + 1)
    if len(content) > max_chars:
        return content[:max_chars] + "\n\n[...truncated...]"
    return content


uploaded_id: str | None = None
try:
    with open(FILE_PATH, "rb") as f:
        uploaded = client.files.create(file=f, purpose="fine-tune")
    uploaded_id = uploaded.id
    print(f"Uploaded file ID: {uploaded_id}")
except NotFoundError:
    # Many OpenAI-compatible local servers don't implement /v1/files.
    print(
        f"Server does not support {BASE_URL}/files (404). Falling back to inlining file content."
    )

if uploaded_id is None:
    file_text = read_text_file(FILE_PATH)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {
                "role": "user",
                "content": (
                    "Please analyze this JSON file content and summarize the key fields and any issues.\n\n"
                    f"Filename: {FILE_PATH}\n\n"
                    f"---\n{file_text}\n---"
                ),
            },
        ],
        temperature=0.2,
    )
    print(response.choices[0].message.content)
