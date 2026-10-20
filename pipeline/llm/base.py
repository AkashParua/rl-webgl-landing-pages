from abc import ABC, abstractmethod
from typing import Any
import json
import re

class LLMClient(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None, **kwargs) -> str:
        """Return plain text response."""
        ...

    def generate_json(self, prompt: str, schema: dict | None = None, **kwargs) -> dict:
        """Generate and parse a JSON response. Override for native structured output."""
        text = self.generate(prompt, **kwargs)
        return self._extract_json(text)

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Best-effort JSON extraction from model output."""
        text = text.strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try to find a JSON object in the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")
