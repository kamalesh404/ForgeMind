"""Central configuration for ForgeMind."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Runtime configuration, overridable via environment variables."""

    host: str = "127.0.0.1"
    port: int = 8080
    backend: str = "ollama"
    model: str = "qwen2.5-coder:7b"
    api_key: str = ""
    max_steps: int = 12
    approval_mode: str = "auto"  # auto | confirm_tools | confirm_all
    trace_dir: str = ".forgemind/traces"
    registry_path: str = ".forgemind/registry.json"

    @classmethod
    def from_env(cls) -> "Config":
        """Build a config from environment variables with sensible defaults."""
        return cls(
            host=os.environ.get("FORGEMIND_HOST", "127.0.0.1"),
            port=int(os.environ.get("FORGEMIND_PORT", "8080")),
            backend=os.environ.get("FORGEMIND_BACKEND", "ollama"),
            model=os.environ.get("FORGEMIND_MODEL", "qwen2.5-coder:7b"),
            api_key=os.environ.get("FORGEMIND_API_KEY", ""),
            max_steps=int(os.environ.get("FORGEMIND_MAX_STEPS", "12")),
            approval_mode=os.environ.get("FORGEMIND_APPROVALS", "auto"),
            trace_dir=os.environ.get("FORGEMIND_TRACE_DIR", ".forgemind/traces"),
            registry_path=os.environ.get("FORGEMIND_REGISTRY", ".forgemind/registry.json"),
        )
