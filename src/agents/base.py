"""Base agent with LLM access and tool calling."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """All ForgeMind agents share an LLM handle and a chat helper."""

    role: str = "agent"
    system_prompt: str = "You are a helpful AI assistant."

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.history: List[Dict[str, str]] = []

    def chat(self, user_input: str, *, temperature: float = 0.3,
             max_tokens: int = 2048) -> str:
        """Send one turn and record it in history."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})
        self.history.append({"role": "user", "content": user_input})
        response = self.llm.chat(messages, temperature=temperature, max_tokens=max_tokens)
        self.history.append({"role": "assistant", "content": response})
        return response

    def reset(self) -> None:
        self.history.clear()

    @staticmethod
    def parse_json_object(text: str) -> Dict[str, Any]:
        """Best-effort extraction of a JSON object from LLM output."""
        import re

        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {}

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's task."""
