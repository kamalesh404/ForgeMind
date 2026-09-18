"""OpenAI-compatible backend — DeepSeek, Together, Groq, vLLM, etc."""

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request
from typing import Any, Dict, List

from src.core.retry import retry_with_backoff
from src.llm.base import LLMBackend

_RETRYABLE = (
    urllib.error.URLError,
    TimeoutError,
    ConnectionError,
    http.client.HTTPException,
    OSError,
)


class OpenAICompatBackend(LLMBackend):
    """POSTs to any /v1/chat/completions endpoint."""

    name = "openai_compat"

    def __init__(self, model: str = "deepseek-chat",
                 base_url: str = "https://api.deepseek.com",
                 api_key: str = "", **kwargs: Any) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or kwargs.get("api_key", "")
        self._loaded = False

    def load(self, model: str | None = None, **kwargs: Any) -> None:
        if model:
            self.model = model
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        if not self.api_key:
            raise ValueError("api_key is required for OpenAI-compatible backends")
        self._loaded = True

    @property
    def loaded(self) -> bool:
        return self._loaded

    @retry_with_backoff(max_retries=3, base_delay=1.0, retryable_exceptions=_RETRYABLE)
    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.3,
             max_tokens: int = 2048) -> str:
        payload = {
            "model": self.model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode())
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return str(data)
