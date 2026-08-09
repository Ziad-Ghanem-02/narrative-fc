import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def ask_llm(prompt: str, model: str = "alias-ha") -> str:
    """Send a prompt through the OpenAI-compatible LLM configured in .env."""
    try:
        api_key = os.environ["OPENAI_API_KEY"]
        base_url = os.environ["OPENAI_BASE_URL"]
    except KeyError as error:
        raise RuntimeError(
            "OPENAI_API_KEY and OPENAI_BASE_URL must be configured."
        ) from error

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content