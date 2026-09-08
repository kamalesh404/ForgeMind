"""Built-in tools registered on every ForgeMind instance."""

from __future__ import annotations

import ast
import datetime
import operator


def register_builtin(registry) -> None:
    """Register the default safe toolset on a registry."""

    @registry.register(
        "calculator",
        "Evaluate a Python arithmetic expression (no names, no calls).",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. (12 + 8) * 3"},
            },
            "required": ["expression"],
        },
    )
    def calculator(expression: str) -> str:
        allowed = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Mod: operator.mod, ast.Pow: operator.pow,
            ast.USub: operator.neg, ast.UAdd: operator.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                return allowed[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
                return allowed[type(node.op)](_eval(node.operand))
            raise ValueError("Only plain arithmetic is allowed.")

        tree = ast.parse(expression, mode="eval")
        return str(_eval(tree))

    @registry.register(
        "current_time",
        "Return the current UTC date and time as ISO-8601.",
        parameters={"type": "object", "properties": {}},
    )
    def current_time() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @registry.register(
        "echo",
        "Echo text back. Useful for testing the tool loop end to end.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )
    def echo(text: str) -> str:
        return text

    @registry.register(
        "word_count",
        "Count words, characters, and lines in a block of text.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )
    def word_count(text: str) -> str:
        words = text.split()
        return f"words={len(words)} chars={len(text)} lines={text.count(chr(10)) + 1}"
