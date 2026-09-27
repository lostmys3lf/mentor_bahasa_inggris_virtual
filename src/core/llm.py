import src.core.env as env

from functools import lru_cache
from google import genai
from google.genai import types


@lru_cache(maxsize=1)
def get_gemini_client():
    gemini_client = genai.Client(
        api_key=env.GEMINI_API_KEY,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=5,
                initial_delay=2,
                max_delay=30,
                exp_base=2,
                http_status_codes=[408, 429, 500, 502, 503, 504],
            )
        ),
    )
    return gemini_client
