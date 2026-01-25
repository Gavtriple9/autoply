import os
from google import genai
from google.genai import errors
import time


def _get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing API key. Set GOOGLE_API_KEY (recommended) or GEMINI_API_KEY."
        )
    return api_key


client = genai.Client(api_key=_get_api_key())


def safe_generate_content(model_id, contents, config):
    retries = 3
    for i in range(retries):
        try:
            return client.models.generate_content(
                model=model_id, contents=contents, config=config
            )
        except errors.ServerError:
            # Handle 500 errors by waiting and retrying
            wait = (i + 1) * 5
            print(f"Server error. Retrying in {wait} seconds...")
            time.sleep(wait)
        except errors.ClientError as e:
            # Handle 429 Quota errors specifically
            if "429" in str(e):
                print("Quota exceeded. Waiting 30 seconds...")
                time.sleep(30)
            else:
                raise e
    raise Exception("Failed after multiple retries due to Server Errors.")


def generate_meal_plan(json_file_path):
    # 1. Upload the file
    print(f"Uploading {json_file_path}...")
    publix_file = client.files.upload(file=json_file_path)

    # 2. Polling to ensure the file is 'ACTIVE' before calling the model
    while publix_file.state.name == "PROCESSING":
        print("Waiting for file to process...")
        time.sleep(2)
        publix_file = client.files.get(name=publix_file.name)

    # 3. Use the confirmed supported model ID
    model_id = "gemini-2.0-flash-lite"

    prompt = """
    You are an expert meal planner.
    Create a 4-day healthy dinner plan for 4 people using the attached Publix deals.
    Include a main protein, a starch, and a fresh vegetable (no frozen/canned).
    Be creative (avoid basic 'meat and potatoes').
    Output ONLY valid JSON in the requested array format.
    """
    config = {"response_mime_type": "application/json"}
    response = safe_generate_content(
        model_id,
        [prompt, publix_file],
        config,
    )

    return response.text


if __name__ == "__main__":
    print(generate_meal_plan("publix.json"))
