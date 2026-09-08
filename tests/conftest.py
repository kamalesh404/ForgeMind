"""Shared test doubles."""

import pytest


class FakeLLM:
    """Scripted LLM: pops canned replies, records prompts."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self._loaded = True

    def load(self, model=None, **kwargs):
        self._loaded = True

    def chat(self, messages, *, temperature=0.3, max_tokens=2048):
        self.calls.append(messages)
        if self.replies:
            return self.replies.pop(0)
        return "{}"

    @property
    def loaded(self):
        return self._loaded


@pytest.fixture
def fake_llm():
    return FakeLLM(['{"thought": "done", "tool_calls": [], "done": true, "final_answer": "ok"}'])
