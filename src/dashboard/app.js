const api = ""; // same origin when served by ForgeMind (/dashboard)

async function checkHealth() {
  const el = document.getElementById("health");
  try {
    const r = await fetch(api + "/health");
    const j = await r.json();
    el.textContent = "API " + j.status + " v" + j.version;
    el.className = "pill ok";
  } catch (e) {
    el.textContent = "API unreachable";
    el.className = "pill bad";
  }
}

document.getElementById("runBtn").addEventListener("click", async () => {
  const out = document.getElementById("runResult");
  out.textContent = "Running...";
  const body = {
    goal: document.getElementById("goal").value,
    max_steps: parseInt(document.getElementById("maxSteps").value, 10),
    approval_mode: document.getElementById("approvalMode").value,
  };
  try {
    const r = await fetch(api + "/v1/runs", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body),
    });
    const j = await r.json();
    out.innerHTML = "<strong>[" + j.status + "]</strong> " +
      (j.steps ? j.steps.length + " steps, " : "") +
      "<pre>" + escapeHtml(j.answer || j.error || JSON.stringify(j)) + "</pre>";
  } catch (e) {
    out.textContent = "Error: " + e;
  }
});

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

let ws = null;
document.getElementById("wsBtn").addEventListener("click", () => {
  const state = document.getElementById("wsState");
  const log = document.getElementById("events");
  if (ws) { ws.close(); ws = null; state.textContent = "disconnected"; return; }
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(proto + "://" + location.host + "/v1/stream");
  ws.onopen = () => { state.textContent = "connected"; state.className = "pill ok"; };
  ws.onclose = () => { state.textContent = "disconnected"; state.className = "pill"; ws = null; };
  ws.onmessage = (ev) => {
    if (log.textContent === "No events yet.") log.textContent = "";
    log.textContent += ev.data + "\n";
    log.scrollTop = log.scrollHeight;
  };
});

document.getElementById("toolsBtn").addEventListener("click", async () => {
  const ul = document.getElementById("tools");
  ul.innerHTML = "<li>Loading...</li>";
  const r = await fetch(api + "/v1/tools");
  const j = await r.json();
  ul.innerHTML = "";
  j.tools.forEach((t) => {
    const li = document.createElement("li");
    li.innerHTML = "<code>" + escapeHtml(t.name) + "</code> — " + escapeHtml(t.description);
    ul.appendChild(li);
  });
});

document.getElementById("tracesBtn").addEventListener("click", async () => {
  const ul = document.getElementById("traces");
  ul.innerHTML = "<li>Loading...</li>";
  const r = await fetch(api + "/v1/traces");
  const j = await r.json();
  ul.innerHTML = "";
  (j.runs || []).forEach((id) => {
    const li = document.createElement("li");
    li.innerHTML = "<code>" + escapeHtml(id) + "</code>";
    ul.appendChild(li);
  });
  if (!j.runs || !j.runs.length) ul.innerHTML = "<li>No traces yet.</li>";
});

checkHealth();
