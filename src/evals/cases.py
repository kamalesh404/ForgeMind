"""Eval cases — small tasks with checkable answers."""

from __future__ import annotations

from typing import Any, Dict, List


def default_cases() -> List[Dict[str, Any]]:
    """Return the built-in eval suite for the default toolset."""
    return [
        {
            "id": "arithmetic",
            "goal": "What is (12 + 8) * 3? Reply with just the number.",
            "must_contain": ["60"],
        },
        {
            "id": "time-format",
            "goal": "What is the current UTC time in ISO format?",
            "must_contain": ["T"],
        },
        {
            "id": "echo-roundtrip",
            "goal": "Echo back exactly this string: forgemind-eval-42",
            "must_contain": ["forgemind-eval-42"],
        },
        {
            "id": "word-count",
            "goal": "How many words are in the sentence 'the quick brown fox'?",
            "must_contain": ["4"],
        },
    ]
