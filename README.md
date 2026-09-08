<div align="center">

# 🧠 ForgeMind

**MCP-native multi-agent AI platform — tools, approvals, traces, evals**

[![License: MIT](https://img.shields.io/badge/License-MIT-FF6F00?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/Protocol-MCP-7C3AED?style=for-the-badge&logo=json&logoColor=white)](docs/mcp.md)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](src/api)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)
[![Tests](https://img.shields.io/badge/Tests-26%20passing-00C853?style=for-the-badge&logo=pytest&logoColor=white)](tests)

**Give it a goal. Planner thinks, Executor acts through MCP tools, Critic verifies — with human approvals and full traces.**

</div>

## Why ForgeMind

2026's AI stack is **agents + MCP + evals**. ForgeMind is a complete, runnable reference implementation of that stack:

- 🔌 **MCP-native** — every tool is exposed as MCP (`tools/list`, `tools/call` over HTTP + stdio); consume any external MCP server too
- 🤝 **Human-in-the-loop** — `auto`, `confirm_tools`, `confirm_all` approval modes for risky tools
- 🔍 **Execution traces** — every run saved as replayable JSON; inspect via CLI, API, or dashboard
- 📊 **Eval harness** — built-in suite with pass-rate reports; add your own cases in one file
- 🖥️ **Live dashboard** — run goals, watch WebSocket events, browse tools and traces
- 🧠 **Any model** — Ollama (free/local), llama.cpp GGUF, or any OpenAI-compatible API

## Architecture

```
Goal → Coordinator (ReAct loop)
         ├── PlannerAgent   → thought + tool_calls (JSON)
         ├── ApprovalGate   → auto / confirm_tools / confirm_all
         ├── ExecutorAgent  → ToolRegistry.execute()
         │                     ├── builtin: calculator, time, echo, word_count
         │                     └── risky: write_file, run_shell, http_request
         ├── CriticAgent    → accept / reject final answer
         └── Tracer         → .forgemind/traces/<run_id>.json

Interfaces: CLI · FastAPI (/v1/runs, /v1/tools, /v1/approvals, /v1/traces)
            MCP endpoint (/v1/mcp) · WebSocket (/v1/stream) · Dashboard (/dashboard)
```

## Quick Start

```bash
pip install -e ".[dev]"

# Needs a model backend — Ollama is free and local:
ollama pull qwen2.5-coder:7b

# Run a goal
forgemind run "What is (12 + 8) * 3? Reply with just the number."

# Start the API + dashboard
forgemind serve
# → http://127.0.0.1:8080/dashboard

# Run evals
forgemind evaluate
```

## API Examples

```bash
# Start a run
curl -X POST localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"goal": "Echo back exactly: hello-forge", "max_steps": 8}'

# List tools (MCP)
curl localhost:8080/v1/tools

# Call a tool via MCP
curl -X POST localhost:8080/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"calculator","arguments":{"expression":"3*7"}}}'

# Pending approvals for a run
curl localhost:8080/v1/approvals/<run_id>
```

## Docker

```bash
docker compose up --build
# API on :8080, data in the forgemind-data volume
```

## CLI Reference

| Command | Purpose |
|---|---|
| `forgemind run "<goal>"` | Execute one goal end to end |
| `forgemind serve` | Start API + dashboard |
| `forgemind evaluate` | Run eval suite, print Markdown report |
| `forgemind tools` | List registered MCP tools |
| `forgemind trace <run_id>` | Print a stored trace |

Env vars: `FORGEMIND_BACKEND`, `FORGEMIND_MODEL`, `FORGEMIND_API_KEY`,
`FORGEMIND_APPROVALS`, `FORGEMIND_MAX_STEPS`, `FORGEMIND_PORT`.

## License

MIT — see [LICENSE](LICENSE)

<div align="center">
<b>Built by <a href="https://github.com/kamalesh404">Kamalesh</a></b>
</div>
