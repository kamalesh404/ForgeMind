"""Ollama backend — free, unlimited local inference."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from src.llm.base import LLMBackend


class OllamaBackend(LLMBackend):
    """Talks to a running Ollama server."""

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "qwen2.5-coder:7b", **kwargs: Any) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._loaded = False

    def load(self, model: str | None = None, **kwargs: Any) -> None:
        if model:
            self.model = model
        self._loaded = True

    @property
    def loaded(self) -> bool:
        return self._loaded

    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.3,
             max_tokens: int = 2048) -> str:
        payload = {
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/chat", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode())
        return data.get("message", {}).get("content", "").strip()
