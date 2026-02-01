import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

# Load .env file (optional)
load_dotenv()


def _is_local_base_url(base_url: str | None) -> bool:
    if not base_url:
        return False
    return "localhost" in base_url or "127.0.0.1" in base_url


def _get_llm_client_and_model() -> tuple[OpenAI, str]:
    """Create an OpenAI SDK client pointed at either OpenAI or a local OpenAI-compatible server.

    Supported env vars:
    - OPENAI_BASE_URL: e.g. http://localhost:11434/v1 (Ollama), http://localhost:1234/v1 (LM Studio)
    - OPENAI_API_KEY: required for OpenAI; for local servers can be omitted
    - MEAL_PLAN_MODEL: model name to use (OpenAI: o3-mini; Ollama: llama3.1:8b-instruct, etc.)
    """

    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        if not _is_local_base_url(base_url):
            raise ValueError(
                "OPENAI_API_KEY is not set. Either set OPENAI_API_KEY for OpenAI, "
                "or set OPENAI_BASE_URL to a local OpenAI-compatible server (e.g. http://localhost:11434/v1)."
            )
        # Local servers typically ignore the key, but the SDK requires a non-empty string.
        client = OpenAI(api_key="local", base_url=base_url)

    model = os.getenv("MEAL_PLAN_MODEL")
    if not model:
        model = "llama3.1:8b-instruct" if _is_local_base_url(base_url) else "o3-mini"

    return client, model


def _extract_json(text: str) -> str:
    """Best-effort extraction of JSON from model output (handles fenced blocks)."""

    s = text.strip()

    fenced = re.search(
        r"```(?:json)?\s*(.*?)\s*```", s, flags=re.DOTALL | re.IGNORECASE
    )
    if fenced:
        return fenced.group(1).strip()

    return s


def generate_meal_plan_with_recipes(deals, family, num_dinners=4, num_people=6):
    """
    Generates a meal plan with step-by-step recipes using deals and user preferences.

    Args:
        deals (list): List of deals, e.g. [{"item": "chicken", "category": "meat", "price": 5.99, "unit": "lb"}]
        family (list): List of user dicts, e.g. [{"name": "Alice", "likes": [], "dislikes": []}]
        num_dinners (int): Number of dinners to plan
        num_people (int): Number of people to feed

    Returns:
        dict: Meal plan JSON including ingredients, total cost, and recipe instructions
    """

    prompt = f"""
You are an expert meal planner and recipe creator.

I need a meal plan for {num_people} people for {num_dinners} dinners.

Family preferences:
{json.dumps(family, indent=2)}

Current deals at Publix:
{json.dumps(deals, indent=2)}

Please generate a meal plan that:
- Feeds all {num_people} people
- Respects likes and dislikes (empty lists = no restrictions)
- Uses items on sale
- Minimizes total cost
- Includes detailed **step-by-step instructions** for each dinner
- Outputs as JSON in this format:
[
    {{
        "dinner": "Grilled Chicken and Broccoli",
        "ingredients": [
            {{"item": "chicken breast", "quantity": "2 lb", "price": 5.99}},
            {{"item": "broccoli", "quantity": "1.5 lb", "price": 2.49}}
        ],
        "instructions": [
            "Step 1: Preheat the oven to 375°F.",
            "Step 2: Season the chicken with salt and pepper.",
            "Step 3: Roast chicken in the oven for 25 minutes.",
            "Step 4: Steam broccoli until tender.",
            "Step 5: Serve chicken with broccoli."
        ],
        "total_cost": 10.47,
    }},
    ...
]

Please calculate quantities per dinner for {num_people} servings and total cost.

Return ONLY valid JSON. Do not wrap in markdown fences. Do not include commentary.
"""

    client, model = _get_llm_client_and_model()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    meal_plan_str = _extract_json(response.choices[0].message.content or "")

    try:
        meal_plan = json.loads(meal_plan_str)
    except json.JSONDecodeError:
        meal_plan = meal_plan_str

    return meal_plan
