let bootstrap = null;
let sessionId = null;
let current = null;
let selectedPersona = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return response.json();
}

function show(id) {
  document.querySelectorAll(".view").forEach((view) => view.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

function optionSourceLabel(source) {
  if (source === "ai") return "AI 动态选择";
  if (source === "local_dynamic") return "本局随机选择";
  return "";
}

function renderPersonas() {
  const root = document.getElementById("personaList");
  root.innerHTML = "";
  bootstrap.personas.forEach((persona) => {
    const card = document.createElement("div");
    card.className = `template-card ${selectedPersona === persona.id ? "active" : ""}`;
    card.innerHTML = `<h3>${persona.name}</h3><p>${persona.desc}</p><p class="muted">${persona.traits.join("、")}</p>`;
    card.addEventListener("click", () => {
      selectedPersona = persona.id;
      document.getElementById("personaName").value = persona.name;
      renderPersonas();
    });
    root.appendChild(card);
  });
}

async function init() {
  bootstrap = await api("/api/bootstrap");
  selectedPersona = bootstrap.personas[0].id;
  renderPersonas();
  document.getElementById("aiStatus").textContent = bootstrap.ai_configured ? "当前已配置 AI。" : "当前未配置 AI，本地随机功能仍可使用。";
}

async function startGame() {
  const payload = {
    template_id: selectedPersona,
    name: document.getElementById("personaName").value.trim() || null,
    custom: document.getElementById("personaCustom").value.trim() || null,
    random_level: document.getElementById("randomLevel").value,
  };
  current = await api("/api/session/start", { method: "POST", body: JSON.stringify(payload) });
  sessionId = current.session_id;
  renderGame();
}

async function refreshSession() {
  if (!sessionId) return;
  current = await api(`/api/session/${sessionId}`);
  renderGame();
}

async function submitChoice(index) {
  current = await api(`/api/session/${sessionId}/choice`, {
    method: "POST",
    body: JSON.stringify({ choice_index: index }),
  });
  if (current.finished) renderReport(current.report);
  else renderGame();
}

async function generateAIChoice() {
  if (!sessionId) return;
  const button = document.getElementById("aiChoice");
  button.disabled = true;
  button.textContent = "AI 生成中...";
  try {
    current = await api(`/api/session/${sessionId}/ai-choice`, { method: "POST", body: "{}" });
    renderGame();
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "生成 AI 额外选择";
  }
}

async function refinePersona() {
  const button = document.getElementById("refinePersona");
  button.disabled = true;
  button.textContent = "AI 优化中...";
  try {
    const data = await api("/api/persona/refine", {
      method: "POST",
      body: JSON.stringify({
        template_id: selectedPersona,
        name: document.getElementById("personaName").value.trim() || null,
        custom: document.getElementById("personaCustom").value.trim() || null,
      }),
    });
    document.getElementById("personaName").value = data.name || document.getElementById("personaName").value;
    document.getElementById("personaCustom").value = data.desc || document.getElementById("personaCustom").value;
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "AI 优化人设";
  }
}

function renderGame() {
  show("game");
  const node = current.node;
  document.getElementById("chapterLabel").textContent = `第 ${node.chapter} 章`;
  document.getElementById("nodeTitle").textContent = node.title;
  document.getElementById("nodeScene").textContent = node.scene;
  document.getElementById("nodeAnchor").textContent = node.anchor;
  const event = current.random_event;
  const eventBox = document.getElementById("randomEvent");
  eventBox.classList.toggle("hidden", !event);
  eventBox.textContent = event ? `本章随机状态：${event.title}。${event.desc}` : "";

  document.getElementById("personaCard").innerHTML = `
    <strong>${current.persona.name}</strong>
    <p>${current.persona.desc}</p>
    <p class="muted">特质：${(current.persona.traits || []).join("、")}</p>
    <p class="muted">随机性：${current.state.randomLevel}</p>
  `;

  const choices = document.getElementById("choices");
  choices.innerHTML = "";
  current.choices.forEach((choice) => {
    const button = document.createElement("button");
    button.className = `choice ${choice.source === "ai" ? "ai" : ""}`;
    const source = optionSourceLabel(choice.source);
    button.innerHTML = `${choice.text}${source ? `<span class="source">${source}</span>` : ""}`;
    button.addEventListener("click", () => submitChoice(choice.index));
    choices.appendChild(button);
  });

  renderBars("resources", current.state.resources, current.labels.resources, 100);
  renderBars("needs", current.state.needs, current.labels.needs, 20);
  renderMap();
}

function renderBars(id, values, labels, scaleMax) {
  const root = document.getElementById(id);
  root.innerHTML = "";
  Object.entries(values).forEach(([key, value]) => {
    const percent = Math.min(100, Math.round((value / scaleMax) * 100));
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `<div class="bar-label"><span>${labels[key]}</span><span>${value}</span></div><div class="bar-track"><div class="bar-fill" style="width:${percent}%"></div></div>`;
    root.appendChild(row);
  });
}

function renderMap() {
  const root = document.getElementById("storyMap");
  root.innerHTML = "";
  for (let i = 1; i <= current.story_count; i++) {
    const done = current.state.choices.some((choice) => choice.chapter === i);
    const mark = done ? "✓" : i === current.node.chapter ? "▶" : "○";
    const div = document.createElement("div");
    div.className = "map-item";
    div.textContent = `${mark} 第 ${i} 章`;
    root.appendChild(div);
  }
}

function renderReport(report) {
  show("report");
  document.getElementById("endingTitle").textContent = report.endingTitle;
  document.getElementById("endingSummary").textContent = report.endingSummary;
  document.getElementById("interpretation").textContent = report.interpretation;
  document.getElementById("topNeeds").textContent = report.topNeeds.join("、");
  document.getElementById("topWounds").textContent = report.topWounds.join("、");
  const list = document.getElementById("styleSummary");
  list.innerHTML = "";
  report.stylesSummary.forEach((line) => {
    const li = document.createElement("li");
    li.textContent = line;
    list.appendChild(li);
  });
}

async function saveAI() {
  try {
    await api("/api/ai/config", {
      method: "POST",
      body: JSON.stringify({
        provider: "deepseek",
        endpoint: document.getElementById("aiEndpoint").value.trim(),
        model: document.getElementById("aiModel").value.trim(),
        api_key: document.getElementById("aiKey").value.trim(),
      }),
    });
    document.getElementById("aiStatus").textContent = "AI 设置已保存。";
  } catch (error) {
    alert(error.message);
  }
}

async function clearAI() {
  await api("/api/ai/config", { method: "DELETE" });
  document.getElementById("aiStatus").textContent = "AI 设置已清除。";
}

document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => show(button.dataset.view)));
document.getElementById("goSetup").addEventListener("click", () => show("setup"));
document.getElementById("startGame").addEventListener("click", startGame);
document.getElementById("refinePersona").addEventListener("click", refinePersona);
document.getElementById("aiChoice").addEventListener("click", generateAIChoice);
document.getElementById("reloadSession").addEventListener("click", refreshSession);
document.getElementById("restart").addEventListener("click", () => show("setup"));
document.getElementById("saveAI").addEventListener("click", saveAI);
document.getElementById("clearAI").addEventListener("click", clearAI);

init().catch((error) => alert(`初始化失败：${error.message}`));
