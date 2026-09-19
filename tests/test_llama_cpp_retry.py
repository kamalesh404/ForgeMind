"""Tests for llama_cpp retry behavior."""

import pytest

from src.llm.llama_cpp import LlamaCppBackend


class FakeLlama:
    """Stand-in for llama_cpp.Llama with scripted failures."""

    def __init__(self, failures):
        self.failures = list(failures)
        self.calls = 0

    def create_completion(self, **kwargs):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return {"choices": [{"text": "  hello  "}]}


def make_backend(failures):
    backend = LlamaCppBackend.__new__(LlamaCppBackend)
    backend._llm = FakeLlama(failures)
    return backend


class TestLlamaCppRetry:
    def test_retries_transient_os_error_then_succeeds(self):
        backend = make_backend([OSError("busy"), OSError("busy")])
        result = backend.chat([{"role": "user", "content": "hi"}])
        assert result == "hello"
        assert backend._llm.calls == 3

    def test_exhausts_retries_on_persistent_failure(self):
        backend = make_backend([OSError("down")] * 5)
        with pytest.raises(OSError, match="down"):
            backend.chat([{"role": "user", "content": "hi"}])
        assert backend._llm.calls == 3  # initial + 2 retries

    def test_deterministic_errors_fail_fast_without_retry(self):
        backend = make_backend([ValueError("bad prompt")])
        with pytest.raises(ValueError, match="bad prompt"):
            backend.chat([{"role": "user", "content": "hi"}])
        assert backend._llm.calls == 1

    def test_not_loaded_guard_raises_before_any_inference(self):
        backend = LlamaCppBackend(model_path=None)
        with pytest.raises(RuntimeError, match="Model not loaded"):
            backend.chat([{"role": "user", "content": "hi"}])
