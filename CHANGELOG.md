# Changelog

All notable changes to ForgeMind are documented here.

## [0.1.0] - 2026-09-12

First public cut of the platform.

### Added
- ReAct coordinator loop: planner, executor, critic agents
- MCP server (JSON-RPC over HTTP and stdio) and MCP client
- Tool registry with JSON-Schema inference and a persisted catalogue
- Built-in tools: calculator, current_time, echo, word_count
- Risky tools: write_file, run_shell, http_request
- Human-in-the-loop approvals: auto, confirm_tools, confirm_all
- Execution tracing to replayable JSON files
- Eval harness with built-in suite and Markdown reports
- FastAPI service: runs, tools, MCP endpoint, approvals, traces
- WebSocket live event stream and static dashboard
- LLM backends: Ollama, llama.cpp, OpenAI-compatible
- CLI: run, serve, evaluate, tools, trace
- Docker and docker-compose deployment
- CI: ruff + pytest across Python 3.9-3.11
