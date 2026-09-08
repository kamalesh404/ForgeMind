"""LLM backend interface and factory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMBackend(ABC):
    """Minimal chat interface every backend implements."""

    name = "base"

    @abstractmethod
    def load(self, model: str | None = None, **kwargs: Any) -> None:
        """Configure / load the model."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.3,
             max_tokens: int = 2048) -> str:
        """Return the assistant reply text."""

    @property
    @abstractmethod
    def loaded(self) -> bool:
        """Whether the backend is ready."""


def create_backend(provider: str, **kwargs: Any) -> LLMBackend:
    """Instantiate a backend by name."""
    provider = provider.lower()
    if provider in ("ollama",):
        from src.llm.ollama import OllamaBackend
        return OllamaBackend(**kwargs)
    if provider in ("openai", "openai_compat", "deepseek", "together"):
        from src.llm.openai_compat import OpenAICompatBackend
        return OpenAICompatBackend(**kwargs)
    if provider in ("llama_cpp", "local", "gguf"):
        from src.llm.llama_cpp import LlamaCppBackend
        return LlamaCppBackend(**kwargs)
    raise ValueError(f"Unknown provider: {provider}")
