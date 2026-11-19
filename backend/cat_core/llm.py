import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from .progress import DATA_DIR

# Load .env from backend folder (and parents for flexibility)
load_dotenv(DATA_DIR.parent / ".env")
load_dotenv()


class MissingApiKeyError(RuntimeError):
    pass


def get_api_key() -> str:
    key = (os.environ.get("ZAI_API_KEY") or "").strip()
    if not key or key == "your_api_key_here":
        raise MissingApiKeyError(
            "ZAI_API_KEY is missing. Copy backend/.env.example to backend/.env and set your key."
        )
    return key


def get_base_url() -> str:
    return os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4/").rstrip("/") + "/"


def get_model_name() -> str:
    return os.environ.get("ZAI_MODEL", "glm-4.5-flash")


def get_vision_model_name() -> str:
    return os.environ.get("ZAI_VISION_MODEL", "glm-4.6v-flash")


@lru_cache(maxsize=1)
def get_chat_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=get_model_name(),
        base_url=get_base_url(),
        api_key=get_api_key(),
        temperature=0.7,
        max_tokens=1500,
        timeout=90,
        max_retries=1,
        use_responses_api=False,
        extra_body={"thinking": {"type": "disabled"}},
    )


def get_vision_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=get_vision_model_name(),
        base_url=get_base_url(),
        api_key=get_api_key(),
        temperature=0,
        timeout=90,
        max_retries=1,
        use_responses_api=False,
        extra_body={"thinking": {"type": "disabled"}},
    )
