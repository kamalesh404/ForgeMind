"""Risky tools — file writing, shell, HTTP. Gated by approvals."""

from __future__ import annotations

import os
import subprocess
import urllib.request


def register_risky(registry, workdir: str = ".") -> None:
    """Register tools that can change the world. Pair with confirm_tools mode."""

    @registry.register(
        "write_file",
        "Write text to a file under the working directory.",
        risky=True,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    )
    def write_file(path: str, content: str) -> str:
        target = os.path.abspath(os.path.join(workdir, path))
        if not target.startswith(os.path.abspath(workdir) + os.sep):
            raise ValueError("Refusing to write outside the working directory.")
        os.makedirs(os.path.dirname(target) or workdir, exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(content)
        return f"Wrote {len(content)} chars to {path}"

    @registry.register(
        "run_shell",
        "Run a shell command with a timeout. Returns stdout/stderr.",
        risky=True,
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout_s": {"type": "string", "description": "Timeout in seconds"},
            },
            "required": ["command"],
        },
    )
    def run_shell(command: str, timeout_s: str = "30") -> str:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=int(timeout_s),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return f"exit={proc.returncode}\n{out[:3000]}"

    @registry.register(
        "http_request",
        "GET a URL and return the first 3000 chars of the response.",
        risky=True,
        parameters={
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    )
    def http_request(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "ForgeMind/0.1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")[:3000]
