# Architecture

## The ReAct loop

`Coordinator.execute_goal(goal)` runs:

```
plan = Planner(goal, tool_descriptions, history)
step = run.add_step(plan.thought)
if plan.done:
    verdict = Critic(goal, plan.final_answer)   # optional
    run.finish(answer) if accepted
else:
    Executor(step, plan):                       # approvals enforced here
        for each tool_call:
            gate.needs_approval(name)? → request human, status=waiting_approval
            registry.execute(name, args) → observation
repeat until done / failed / max_steps
```

## Components

- `src/agents/` — planner, executor, critic, coordinator. Agents only talk
  JSON to each other; the coordinator owns all control flow.
- `src/mcp/` — registry (tools + JSON schemas), MCP server (JSON-RPC),
  MCP client (call external servers).
- `src/core/` — run model, tracer (JSON persistence), approvals gate, config.
- `src/llm/` — backend interface + ollama / llama.cpp / OpenAI-compatible.
- `src/api/` — FastAPI: runs, tools, MCP endpoint, approvals, traces,
  WebSocket fan-out, static dashboard.
- `src/evals/` — cases, metrics, harness with Markdown reports.
- `src/tools/` — builtin (safe) and risky (approval-gated) tools.

## Why this shape

Deterministic orchestration, generative agents. The loop, approvals, and
persistence are plain code you can test (26 tests, no model needed); only the
thinking is delegated to the LLM. Swap models without touching the pipeline.
