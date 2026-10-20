import os
from .base import LLMClient
from .ollama import OllamaClient
from .openai_compat import OpenAICompatibleClient

def get_client(config: dict | None = None) -> LLMClient:
    """Return the configured LLM client based on environment variables.

    LLM_PROVIDER: ollama | openai | anthropic | groq | openrouter | custom
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return OllamaClient(
            model=os.getenv("OLLAMA_MODEL"),
            base_url=os.getenv("OLLAMA_BASE_URL"),
        )
    elif provider in ("openai", "anthropic", "groq", "openrouter", "custom", "together"):
        return OpenAICompatibleClient(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            "Supported: ollama, openai, groq, openrouter, custom, together"
        )
