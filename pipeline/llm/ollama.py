import os
from typing import Any
import ollama
from .base import LLMClient

class OllamaClient(LLMClient):
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.temperature = temperature
        self.max_tokens = max_tokens
        # ollama client respects OLLAMA_HOST if set; we can also pass host explicitly if needed

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        options = {
            "temperature": kwargs.get("temperature", self.temperature),
            "num_predict": kwargs.get("max_tokens", self.max_tokens),
        }

        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=options,
        )
        return response["message"]["content"]
