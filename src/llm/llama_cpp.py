"""llama.cpp backend — local GGUF with 4GB-VRAM-friendly defaults."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.retry import retry_with_backoff
from src.llm.base import LLMBackend

# Only genuinely transient failures are retried. Deterministic errors
# (model not loaded, context overflow, bad prompt) must fail fast.
_TRANSIENT_INFERENCE_ERRORS = (ConnectionError, TimeoutError, OSError)


class LlamaCppBackend(LLMBackend):
    """Wraps llama-cpp-python. Set n_gpu_layers low on small GPUs."""

    name = "llama_cpp"

    def __init__(self, model_path: str | None = None, **kwargs: Any) -> None:
        self.model_path = model_path
        self.options = kwargs
        self._llm = None
        self._loaded = False

    def load(self, model: str | None = None, **kwargs: Any) -> None:
        from llama_cpp import Llama

        path = model or self.model_path
        if not path:
            raise ValueError("model path is required for llama_cpp backend")
        n_gpu = kwargs.get("n_gpu_layers", self.options.get("n_gpu_layers", 0))
        self._llm = Llama(
            model_path=path,
            n_ctx=self.options.get("n_ctx", 8192),
            n_gpu_layers=n_gpu,
            n_threads=self.options.get("n_threads", 8),
            verbose=False,
        )
        self.model_path = path
        self._loaded = True

    @property
    def loaded(self) -> bool:
        return self._loaded

    @staticmethod
    def _prompt(messages: List[Dict[str, str]]) -> str:
        parts = []
        for m in messages:
            role = m.get("role", "user")
            parts.append(f"<|im_start|>{role}\n{m.get('content', '')}<|im_end|>")
        parts.append("<|im_start|>assistant\n")
        return "\n".join(parts)

    def chat(
        self, messages: List[Dict[str, str]], *, temperature: float = 0.3, max_tokens: int = 2048
    ) -> str:
        if not self._llm:
            raise RuntimeError("Model not loaded. Call load() first.")
        return self._complete_with_retry(
            self._prompt(messages), temperature=temperature, max_tokens=max_tokens
        )

    @retry_with_backoff(
        max_retries=2, base_delay=0.5, retryable_exceptions=_TRANSIENT_INFERENCE_ERRORS
    )
    def _complete_with_retry(self, prompt: str, temperature: float, max_tokens: int) -> str:
        out = self._llm.create_completion(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=["<|im_end|>", "<|im_start|>"],
        )
        return out["choices"][0]["text"].strip()
