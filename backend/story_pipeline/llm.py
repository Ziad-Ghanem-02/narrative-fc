import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, OpenAI


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

# The story pipeline runs for several minutes and makes many LLM calls, so a
# single transient drop from the provider (e.g. "Server disconnected without
# sending a response") should not kill the whole run. These retries sit on top
# of the OpenAI client's own (short, low-attempt) retry logic.
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 4
REQUEST_TIMEOUT_SECONDS = 300

# Errors that are worth retrying: the server hung up, timed out, or returned a
# transient 5xx. Non-transient failures (auth, bad request) still surface.
_RETRYABLE = (APIConnectionError, APITimeoutError)


def ask_llm(prompt: str, model: str = "openai/gpt-oss-120b") -> str:
    """Send a prompt through the OpenAI-compatible LLM configured in .env.

    Retries transient connection/timeout failures with exponential backoff so
    a flaky upstream does not abort a long-running story generation job.
    """
    try:
        api_key = os.environ["OPENAI_API_KEY"]
        base_url = os.environ["OPENAI_BASE_URL"]
    except KeyError as error:
        raise RuntimeError(
            "OPENAI_API_KEY and OPENAI_BASE_URL must be configured."
        ) from error

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=0,  # we handle retries ourselves for longer backoff
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
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
        except _RETRYABLE as error:
            last_error = error
            if attempt == MAX_RETRIES:
                break
            wait = RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "LLM call failed (attempt %d/%d): %s. Retrying in %ds.",
                attempt,
                MAX_RETRIES,
                error,
                wait,
            )
            time.sleep(wait)

    raise last_error  # type: ignore[misc]