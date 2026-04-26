const DATA = window.LIFE_ECHO_DATA;
const STORAGE_KEY = "life_echo_web_state";
const ARCHIVE_KEY = "life_echo_web_archive";
const AI_SETTINGS_KEY = "life_echo_ai_settings";

const PERSONA_TEMPLATES = [
  {
    id: "careful_achiever",
    name: "谨慎的好学生",
    desc: "习惯提前准备，害怕出错，容易把结果和价值感绑在一起。",
    traits: ["谨慎", "高标准", "怕否定"],
    modifiers: {
      resources: { career: 5, energy: -3, stability: -2 },
      wounds: { worth: 5, control: 3 },
      needs: { achievement: 4, safety: 3 },
      styles: { reflect: 2, selfBlame: 1 },
      tags: ["persona_achiever"],
    },
  },
  {
    id: "quiet_observer",
    name: "安静的观察者",
    desc: "很会察言观色，不轻易表达真实需要，关系里的细微变化会被放大。",
    traits: ["敏感", "克制", "怕打扰"],
    modifiers: {
      resources: { relationship: 2, stability: -2 },
      wounds: { abandonment: 4, neglect: 4 },
      needs: { seen: 4, belonging: 3 },
      styles: { avoid: 2, solo: 1 },
      tags: ["persona_observer"],
    },
  },
  {
    id: "warm_connector",
    name: "温暖的连接者",
    desc: "重视关系和回应，愿意靠近别人，也容易为了维持气氛委屈自己。",
    traits: ["重情感", "会照顾人", "怕失去"],
    modifiers: {
      resources: { relationship: 6, energy: -2 },
      wounds: { abandonment: 3, overload: 2 },
      needs: { belonging: 5, seen: 3 },
      styles: { please: 2, seekHelp: 1 },
      tags: ["persona_connector"],
    },
  },
  {
    id: "restless_explorer",
    name: "不安分的探索者",
    desc: "更在意自由和可能性，能接受不确定，也更容易被波动消耗。",
    traits: ["自主", "好奇", "不耐束缚"],
    modifiers: {
      resources: { career: 2, stability: -4, energy: 2 },
      wounds: { control: 3, rejection: 2 },
      needs: { autonomy: 6, achievement: 2 },
      styles: { self: 2, face: 1 },
      tags: ["persona_explorer"],
    },
  },
  {
    id: "tired_responsible",
    name: "早熟的承担者",
    desc: "很早学会懂事和补位，可靠，但不太知道什么时候可以停下来。",
    traits: ["负责", "能扛", "容易透支"],
    modifiers: {
      resources: { career: 3, energy: -6, relationship: 2 },
      wounds: { overload: 6, neglect: 2 },
      needs: { recovery: 5, safety: 2 },
      styles: { solo: 2, please: 1 },
      tags: ["persona_responsible"],
    },
  },
  {
    id: "self_rebuilder",
    name: "正在重建的人",
    desc: "已经隐约意识到旧模式存在，希望这一局更早看见自己。",
    traits: ["反思", "修复", "边界"],
    modifiers: {
      resources: { stability: 4, energy: 2 },
      wounds: { worth: -2, overload: -1 },
      needs: { autonomy: 4, recovery: 4, seen: 2 },
      styles: { reflect: 2, flexible: 2 },
      tags: ["persona_rebuilder"],
    },
  },
];

const RANDOM_EVENTS = [
  {
    title: "今天特别想被肯定",
    desc: "你比平时更在意别人的语气，哪怕一句普通评价也容易在心里停很久。",
    weightTags: ["early_shame", "rank_internalized", "persona_achiever"],
    effects: { wounds: { worth: 2, rejection: 1 }, needs: { seen: 2 } },
  },
  {
    title: "身体先替你喊了停",
    desc: "你没有明显崩溃，只是突然很累，连回复消息都像要从很远的地方把自己拽回来。",
    weightTags: ["keep_carrying", "persona_responsible", "after_hours_compliance"],
    effects: { resources: { energy: -4, stability: -1 }, needs: { recovery: 3 } },
  },
  {
    title: "有人给了你意外的善意",
    desc: "一个并不隆重的回应，让你短暂地感觉自己没有那么孤单。",
    weightTags: ["child_reached_peer", "rank_shared", "persona_connector"],
    effects: { resources: { relationship: 3, stability: 2 }, needs: { belonging: 2 } },
  },
  {
    title: "你突然很想自己做主",
    desc: "不是为了反抗谁，而是某个瞬间你清楚地知道：这件事不能再只按别人的期待来。",
    weightTags: ["persona_explorer", "child_asked_chance", "boundary_stated"],
    effects: { needs: { autonomy: 3 }, styles: { self: 1 } },
  },
  {
    title: "旧记忆轻轻冒头",
    desc: "眼前的场景让你想起更早以前的某个时刻，你没有完全被拉回去，但心里确实颤了一下。",
    weightTags: ["child_hidden_mistake", "child_unpicked_memory", "early_surface_peace"],
    effects: { wounds: { abandonment: 1, neglect: 1, worth: 1 }, needs: { safety: 2 } },
  },
];

const LOCAL_DYNAMIC_CHOICES = [
  {
    text: "先不急着选，写下一句此刻最真实的感受。",
    effects: { resources: { stability: 3 }, needs: { seen: 2, recovery: 1 }, styles: { reflect: 2 }, tags: ["dynamic_self_note"] },
  },
  {
    text: "问问自己：这个选择是在保护我，还是在惩罚我？",
    effects: { resources: { stability: 4 }, wounds: { worth: -1 }, needs: { autonomy: 2 }, styles: { flexible: 2, reflect: 1 }, tags: ["dynamic_pattern_check"] },
  },
  {
    text: "给一个可信的人发出很短的求助信号。",
    effects: { resources: { relationship: 3, stability: 2 }, needs: { belonging: 2, seen: 2 }, styles: { seekHelp: 2 }, tags: ["dynamic_reach_out"] },
  },
  {
    text: "允许自己选一个不那么完美、但更能呼吸的方案。",
    effects: { resources: { energy: 3, stability: 2, career: -1 }, needs: { recovery: 3, autonomy: 2 }, styles: { flexible: 2, self: 1 }, tags: ["dynamic_breathable_choice"] },
  },
];

let state = loadState() || createInitialState();
let latestReport = null;
let selectedPersonaId = PERSONA_TEMPLATES[0].id;
let currentDynamicChoices = [];

function nowStr() {
  return new Date().toLocaleString("zh-CN", { hour12: false });
}

function clamp(n, min = 0, max = 100) {
  return Math.max(min, Math.min(max, n));
}

function createInitialState() {
  return {
    startedAt: nowStr(),
    nodeIndex: 0,
    finished: false,
    seed: Math.floor(Math.random() * 1000000000),
    randomLevel: "medium",
    persona: null,
    randomEvents: {},
    dynamicChoices: {},
    resources: { career: 50, money: 50, energy: 60, relationship: 50, stability: 55 },
    wounds: { rejection: 20, abandonment: 20, control: 20, overload: 20, neglect: 20, worth: 20 },
    needs: { safety: 0, seen: 0, control: 0, belonging: 0, autonomy: 0, achievement: 0, recovery: 0 },
    styles: { face: 0, avoid: 0, self: 0, please: 0, seekHelp: 0, solo: 0, reflect: 0, impulse: 0, flexible: 0, selfBlame: 0 },
    tags: [],
    choices: [],
    unlockedAchievements: [],
    chapterSummaries: [],
  };
}

function applyEffects(targetState, effects = {}) {
  Object.entries(effects.resources || {}).forEach(([key, value]) => {
    targetState.resources[key] = clamp((targetState.resources[key] || 0) + value);
  });
  Object.entries(effects.wounds || {}).forEach(([key, value]) => {
    targetState.wounds[key] = clamp((targetState.wounds[key] || 0) + value);
  });
  Object.entries(effects.needs || {}).forEach(([key, value]) => {
    targetState.needs[key] = clamp((targetState.needs[key] || 0) + value, 0, 999);
  });
  Object.entries(effects.styles || {}).forEach(([key, value]) => {
    targetState.styles[key] = (targetState.styles[key] || 0) + value;
  });
  if (effects.tags) targetState.tags.push(...effects.tags);
}

function createStateFromSetup() {
  const template = PERSONA_TEMPLATES.find((item) => item.id === selectedPersonaId) || PERSONA_TEMPLATES[0];
  const name = document.getElementById("personaName").value.trim() || template.name;
  const custom = document.getElementById("personaCustom").value.trim();
  const randomLevel = document.getElementById("randomLevel").value;
  const next = createInitialState();
  next.randomLevel = randomLevel;
  next.persona = {
    id: template.id,
    name,
    baseName: template.name,
    desc: custom || template.desc,
    traits: template.traits,
    custom,
  };
  applyEffects(next, template.modifiers);
  if (custom) {
    next.tags.push("persona_custom");
    next.needs.seen += 2;
    next.styles.reflect += 1;
  }
  return next;
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

function clearState() {
  localStorage.removeItem(STORAGE_KEY);
}

function showView(id) {
  document.querySelectorAll(".view").forEach((view) => view.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

function choiceIsAvailable(choice) {
  const tags = new Set(state.tags);
  const any = choice.requiresAnyTags || [];
  const all = choice.requiresAllTags || [];
  const excluded = choice.excludesAnyTags || [];
  if (any.length && !any.some((tag) => tags.has(tag))) return false;
  if (all.length && !all.every((tag) => tags.has(tag))) return false;
  if (excluded.some((tag) => tags.has(tag))) return false;
  return true;
}

function levelChance() {
  if (state.randomLevel === "low") return 0.25;
  if (state.randomLevel === "high") return 0.75;
  return 0.48;
}

function weightedEvents() {
  const tags = new Set(state.tags);
  return RANDOM_EVENTS.flatMap((event) => {
    const weight = 1 + (event.weightTags || []).filter((tag) => tags.has(tag)).length * 2;
    return Array.from({ length: weight }, () => event);
  });
}

function ensureRandomEventForNode(node) {
  if (Object.prototype.hasOwnProperty.call(state.randomEvents, node.chapter)) {
    return state.randomEvents[node.chapter];
  }
  if (Math.random() > levelChance()) {
    state.randomEvents[node.chapter] = null;
    saveState();
    return null;
  }
  const pool = weightedEvents();
  const event = { ...pool[Math.floor(Math.random() * pool.length)] };
  state.randomEvents[node.chapter] = event;
  applyEffects(state, event.effects);
  saveState();
  return event;
}

function shuffleForThisRender(items) {
  const result = [...items];
  const intensity = state.randomLevel === "high" ? 1 : state.randomLevel === "medium" ? 0.55 : 0.15;
  if (Math.random() > intensity) return result;
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function localDynamicChoice() {
  const base = LOCAL_DYNAMIC_CHOICES[Math.floor(Math.random() * LOCAL_DYNAMIC_CHOICES.length)];
  return { ...base, source: "local_dynamic" };
}

function ensureDynamicChoices(node) {
  const cached = state.dynamicChoices[node.chapter] || [];
  currentDynamicChoices = cached;
  if (!cached.length && Math.random() < levelChance()) {
    const choice = localDynamicChoice();
    state.dynamicChoices[node.chapter] = [choice];
    currentDynamicChoices = [choice];
    saveState();
  }
  return currentDynamicChoices;
}

function currentNode() {
  return DATA.storyNodes[state.nodeIndex];
}

function applyChoice(choice, choiceIndex) {
  const node = currentNode();
  const effects = choice.effects || {};
  applyEffects(state, effects);
  state.choices.push({
    nodeId: node.id,
    nodeTitle: node.title,
    choiceIndex,
    choiceText: choice.text,
    choiceSource: choice.source || "story",
    chapter: node.chapter,
    at: nowStr(),
  });
  if (choice.unlockAchievement && !state.unlockedAchievements.includes(choice.unlockAchievement)) {
    state.unlockedAchievements.push(choice.unlockAchievement);
  }
  if (node.chapter === 1 && !state.unlockedAchievements.includes("first_step")) {
    state.unlockedAchievements.push("first_step");
  }
  state.chapterSummaries = state.chapterSummaries.filter((item) => item.chapter !== node.chapter);
  state.chapterSummaries.push(buildChapterMirror(node.chapter));
  state.nodeIndex += 1;
  state.finished = state.nodeIndex >= DATA.storyNodes.length;
  saveState();
}

function topKey(obj) {
  return Object.entries(obj).sort((a, b) => b[1] - a[1])[0][0];
}

function buildChapterMirror(chapter) {
  const wound = topKey(state.wounds);
  const need = topKey(state.needs);
  const lines = [];
  if (wound === "control") lines.push("这一章里，你对“不要失控”的在意很明显。你做的很多选择，更像是在提前阻止最坏情况发生。");
  if (wound === "abandonment") lines.push("这一章里，关系中的不确定感对你的影响很大。你害怕的也许不是某个人离开，而是再次站在不被选择的位置。");
  if (wound === "worth") lines.push("这一章里，你很容易把结果和自我价值绑在一起。失败本来只是一次事件，却容易被听成对自己的判词。");
  if (wound === "overload") lines.push("这一章里，你像那个总会自动补位的人。长期扛责会让你逐渐分不清哪些本来不该全由你承担。");
  if (need === "recovery") lines.push("你这一章真正缺的，可能不是再努力一点，而是恢复一点。");
  if (need === "seen") lines.push("你这一章真正想要的，不一定是建议，而是被认真看见。");
  if (need === "autonomy") lines.push("你这一章明显在争取“由我来决定”。");
  if (!lines.length) lines.push("这一章里，你没有完全被某一种模式牵着走。你在犹豫、权衡和试探中前进。");
  return { chapter, title: `第 ${chapter} 章镜像`, content: lines.slice(0, 2).join(" ") };
}

function determineEnding() {
  const r = state.resources;
  const w = state.wounds;
  const s = state.styles;
  const n = state.needs;
  if (state.tags.includes("active_repair") || (state.tags.includes("self_returned") && s.flexible >= s.selfBlame && n.recovery >= 18)) return "quiet_repair";
  if (state.tags.includes("self_returned") && n.autonomy >= 18 && r.stability >= 55) return "integrated_self";
  if (r.career >= 72 && r.stability <= 40 && w.neglect >= 30 && s.please >= s.self) return "hollow_success";
  if (n.autonomy >= 16 && r.stability < 55 && state.tags.includes("uncertain_but_true")) return "free_but_unstable";
  if (s.please >= 4 && n.belonging >= 10 && r.relationship >= 55 && r.stability <= 50) return "everyone_happy_except_you";
  if (r.energy <= 38 && w.overload >= 28) return "exhausted_survivor";
  if (r.relationship >= 65 && n.seen + n.belonging >= 20) return "connected_and_warm";
  return "delayed_bloom";
}

function computeAchievements(endingId) {
  const unlocked = new Set(state.unlockedAchievements);
  const safeTags = state.tags.filter((tag) => ["safe_path", "safe_future", "family_approved"].includes(tag)).length;
  const freedomTags = state.tags.filter((tag) => ["autonomy_path", "uncertain_but_true", "boundary_at_work", "family_boundary", "self_returned"].includes(tag)).length;
  if ((state.styles.seekHelp || 0) <= 1) unlocked.add("no_one_bothered");
  if (safeTags >= 2) unlocked.add("hold_everything");
  if (freedomTags >= 2) unlocked.add("freedom_over_safety");
  if (state.resources.energy <= 30 && state.finished) unlocked.add("still_standing");
  if (state.resources.relationship >= 62) unlocked.add("soft_connection");
  if (endingId === "hollow_success") unlocked.add("hidden_branch_hollow");
  if (state.tags.includes("pattern_named") || state.tags.includes("borrowed_answer_seen")) unlocked.add("pattern_seen");
  if (state.tags.includes("need_spoken_clearly")) unlocked.add("asked_clearly");
  if (state.tags.includes("repair_begins") || state.tags.includes("active_repair") || endingId === "quiet_repair") unlocked.add("repair_begins");
  if (state.tags.includes("self_returned") || endingId === "integrated_self") unlocked.add("return_to_self");
  return [...unlocked].sort();
}

function buildReport() {
  const endingId = determineEnding();
  const ending = DATA.endings[endingId];
  const needs = Object.entries(state.needs).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([key]) => DATA.labels.needs[key]);
  const wounds = Object.entries(state.wounds).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([key]) => DATA.labels.wounds[key]);
  const s = state.styles;
  const styleSummary = [
    s.face >= s.avoid ? "你多数时候更倾向于面对问题，而不是完全躲开。" : "你更容易先回避不适，等情绪下降后再处理问题。",
    s.self >= s.please ? "在关键节点里，你更愿意争取自己的边界。" : "在关键节点里，你更容易优先维持关系与气氛。",
    s.seekHelp >= s.solo ? "你并非总是独自承担，必要时会尝试向外连接。" : "你很习惯自己消化压力，这让你显得可靠，也更容易被忽略。",
    s.flexible >= s.selfBlame ? "你在部分节点里已经开始把失败与自我价值分开。" : "你仍然容易把不顺利听成对自己的否定。",
  ];
  const interpretation = buildInterpretation(needs, wounds);
  return {
    id: Date.now().toString(),
    createdAt: nowStr(),
    endingId,
    endingTitle: ending.title,
    endingSummary: ending.summary,
    topNeeds: needs,
    topWounds: wounds,
    styleSummary,
    interpretation,
    achievements: computeAchievements(endingId),
  };
}

function buildInterpretation(needs, wounds) {
  const parts = [];
  if (wounds.includes("失控恐惧")) parts.push("你反复在意的，往往不是单一结果，而是局面脱离掌控后的连锁后果。");
  if (wounds.includes("遗弃敏感")) parts.push("关系中的模糊、冷淡和未被回应，对你的影响比你表面表现出来的更大。");
  if (wounds.includes("价值感脆弱")) parts.push("你在多个节点里把结果与自我价值绑得比较紧。");
  if (wounds.includes("责任过载")) parts.push("你习惯补位、扛责、维持运转，但别人也容易默认你还能继续承担。");
  if (needs.includes("休息与修复")) parts.push("你当前最缺的也许不是新的目标，而是恢复。");
  if (needs.includes("被看见")) parts.push("你当前明显需要被理解，而不是再被指导一次。");
  if (needs.includes("自主与边界")) parts.push("你现在很需要替自己做主。");
  return parts.length ? parts.join(" ") : "你的这局人生并没有被一种模式完全垄断。你在矛盾中尝试了不同路径。";
}

function renderGame() {
  const node = currentNode();
  const event = ensureRandomEventForNode(node);
  const dynamicChoices = ensureDynamicChoices(node);
  showView("gameView");
  document.getElementById("chapterLabel").textContent = `第 ${node.chapter} 章 · ${state.startedAt}`;
  document.getElementById("nodeTitle").textContent = node.title;
  document.getElementById("nodeScene").textContent = node.scene;
  document.getElementById("nodeAnchor").textContent = node.anchor;
  const eventBox = document.getElementById("randomEvent");
  eventBox.classList.toggle("hidden", !event);
  eventBox.textContent = event ? `本章随机状态：${event.title}。${event.desc}` : "";
  const previous = state.chapterSummaries.find((item) => item.chapter === node.chapter - 1);
  const mirror = document.getElementById("previousMirror");
  mirror.classList.toggle("hidden", !previous);
  mirror.textContent = previous ? `${previous.title}：${previous.content}` : "";

  const choices = document.getElementById("choices");
  choices.innerHTML = "";
  const availableStoryChoices = node.choices
    .map((choice, index) => ({ choice, index }))
    .filter(({ choice }) => choiceIsAvailable(choice));
  const mergedChoices = [
    ...availableStoryChoices,
    ...dynamicChoices.map((choice, offset) => ({ choice, index: 1000 + offset })),
  ];
  shuffleForThisRender(mergedChoices).forEach(({ choice, index }) => {
    if (!choiceIsAvailable(choice)) return;
    const button = document.createElement("button");
    button.className = `choice ${choice.source === "ai" ? "ai-choice" : ""}`;
    const sourceLabel = choice.source === "ai" ? "AI 动态选择" : choice.source === "local_dynamic" ? "本局随机选择" : "";
    button.innerHTML = `${choice.text}${sourceLabel ? `<span class="choice-meta">${sourceLabel}</span>` : ""}`;
    button.addEventListener("click", () => {
      applyChoice(choice, index);
      if (state.finished) {
        latestReport = buildReport();
        clearState();
        renderReport(latestReport);
      } else {
        renderGame();
      }
    });
    choices.appendChild(button);
  });
  renderPersonaCard();
  renderBars("resources", state.resources, DATA.labels.resources, 100);
  renderBars("needs", state.needs, DATA.labels.needs, 20);
  renderStoryMap();
}

function renderPersonaCard() {
  const root = document.getElementById("personaCard");
  const persona = state.persona || { name: "未设定", desc: "本局未使用人设初始化。", traits: [] };
  root.innerHTML = `
    <strong>${persona.name}</strong>
    <span>${persona.baseName ? `基础：${persona.baseName}` : ""}</span>
    <span>${persona.desc}</span>
    <span>特质：${(persona.traits || []).join("、") || "无"}</span>
    <span>随机性：${state.randomLevel === "high" ? "高" : state.randomLevel === "low" ? "低" : "中"}</span>
  `;
}

function renderBars(id, values, labels, scaleMax) {
  const root = document.getElementById(id);
  root.innerHTML = "";
  Object.entries(values).forEach(([key, value]) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    const percent = Math.min(100, Math.round((value / scaleMax) * 100));
    row.innerHTML = `<div class="bar-label"><span>${labels[key]}</span><span>${value}</span></div><div class="bar-track"><div class="bar-fill" style="width:${percent}%"></div></div>`;
    root.appendChild(row);
  });
}

function renderStoryMap() {
  const root = document.getElementById("storyMap");
  root.innerHTML = "";
  const current = currentNode();
  DATA.storyNodes.forEach((node) => {
    const done = state.choices.some((choice) => choice.chapter === node.chapter);
    const mark = done ? "✓" : current && current.chapter === node.chapter ? "▶" : "○";
    const div = document.createElement("div");
    div.className = "map-item";
    div.textContent = `${mark} 第 ${node.chapter} 章：${node.title}`;
    root.appendChild(div);
  });
}

function loadAiSettings() {
  try {
    return JSON.parse(localStorage.getItem(AI_SETTINGS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveAiSettings() {
  const settings = {
    endpoint: document.getElementById("aiEndpoint").value.trim(),
    model: document.getElementById("aiModel").value.trim(),
    key: document.getElementById("aiKey").value.trim(),
  };
  localStorage.setItem(AI_SETTINGS_KEY, JSON.stringify(settings));
  alert("AI 设置已保存。");
}

function renderAiSettings() {
  const settings = loadAiSettings();
  document.getElementById("aiEndpoint").value = settings.endpoint || "";
  document.getElementById("aiModel").value = settings.model || "";
  document.getElementById("aiKey").value = settings.key || "";
  showView("settingsView");
}

async function generateAiChoice() {
  const settings = loadAiSettings();
  if (!settings.endpoint || !settings.model || !settings.key) {
    alert("还没有配置 AI 接口。你可以在“AI设置”里填写，或继续使用本地随机选项。");
    return;
  }
  const node = currentNode();
  const prompt = [
    "你是一个互动叙事游戏的选项生成器。",
    "请基于用户人设、当前人生节点和状态，生成一个新的可选行动。",
    "要求：中文，40字以内，像游戏选择按钮；不要说教；不要诊断；不要输出解释。",
    "只输出 JSON：{\"text\":\"...\"}",
    `人设：${JSON.stringify(state.persona)}`,
    `当前节点：${node.title}｜${node.scene}`,
    `资源：${JSON.stringify(state.resources)}`,
    `需求：${JSON.stringify(state.needs)}`,
    `受伤线索：${JSON.stringify(state.wounds)}`,
  ].join("\n");

  const button = document.getElementById("aiChoiceBtn");
  button.disabled = true;
  button.textContent = "AI 生成中...";
  try {
    const response = await fetch(settings.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${settings.key}`,
      },
      body: JSON.stringify({
        model: settings.model,
        messages: [
          { role: "system", content: "你只输出严格 JSON，不输出 Markdown。" },
          { role: "user", content: prompt },
        ],
        temperature: 0.9,
      }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const raw = data.choices?.[0]?.message?.content || "";
    const parsed = JSON.parse(raw.replace(/^```json|```$/g, "").trim());
    const aiChoice = {
      text: parsed.text || "按此刻更真实的需要做一个小决定。",
      source: "ai",
      effects: {
        resources: { stability: 2 },
        needs: { seen: 2, autonomy: 1 },
        styles: { reflect: 1, face: 1 },
        tags: ["ai_dynamic_choice"],
      },
    };
    const list = state.dynamicChoices[node.chapter] || [];
    list.push(aiChoice);
    state.dynamicChoices[node.chapter] = list;
    currentDynamicChoices = list;
    saveState();
    renderGame();
  } catch (error) {
    alert(`AI 生成失败：${error.message}\n可能是 Key、接口地址、模型名或浏览器跨域限制导致。`);
  } finally {
    button.disabled = false;
    button.textContent = "生成 AI 额外选择";
  }
}

function ensureAiReady() {
  const settings = loadAiSettings();
  if (!settings.endpoint || !settings.model || !settings.key) {
    alert("还没有配置 AI 接口。请先进入“AI设置”，可点击 DeepSeek 预设后粘贴你的 API Key。");
    return null;
  }
  return settings;
}

async function callChatCompletion(prompt, temperature = 0.8) {
  const settings = ensureAiReady();
  if (!settings) return null;
  const response = await fetch(settings.endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${settings.key}`,
    },
    body: JSON.stringify({
      model: settings.model,
      messages: [
        { role: "system", content: "你只输出严格 JSON，不输出 Markdown，不输出多余解释。" },
        { role: "user", content: prompt },
      ],
      temperature,
    }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  const raw = data.choices?.[0]?.message?.content || "";
  return JSON.parse(raw.replace(/^```json|```$/g, "").trim());
}

async function refinePersonaWithAi() {
  const template = PERSONA_TEMPLATES.find((item) => item.id === selectedPersonaId) || PERSONA_TEMPLATES[0];
  const currentName = document.getElementById("personaName").value.trim() || template.name;
  const currentCustom = document.getElementById("personaCustom").value.trim();
  const button = document.getElementById("aiPersonaBtn");
  button.disabled = true;
  button.textContent = "AI 生成中...";
  try {
    const prompt = [
      "请为一个现实人生模拟游戏生成开局人设。",
      "要求：温和、具体、有可玩性；不要诊断；不要使用病理标签；不要超过120字。",
      "只输出 JSON：{\"name\":\"...\",\"desc\":\"...\",\"traits\":[\"...\",\"...\",\"...\"]}",
      `基础模板：${template.name}｜${template.desc}`,
      `用户输入名字：${currentName}`,
      `用户补充：${currentCustom || "无"}`,
    ].join("\n");
    const parsed = await callChatCompletion(prompt, 0.85);
    if (!parsed) return;
    document.getElementById("personaName").value = parsed.name || currentName;
    document.getElementById("personaCustom").value = parsed.desc || currentCustom || template.desc;
    if (Array.isArray(parsed.traits) && parsed.traits.length) {
      const customTemplate = PERSONA_TEMPLATES.find((item) => item.id === selectedPersonaId);
      if (customTemplate) customTemplate.traits = parsed.traits.slice(0, 4);
      renderPersonaTemplates();
    }
  } catch (error) {
    alert(`AI 优化人设失败：${error.message}\n如果你是直接双击 HTML 打开的，浏览器可能会拦截跨域请求；这种情况下需要用后端代理或继续使用本地随机人设。`);
  } finally {
    button.disabled = false;
    button.textContent = "AI 优化人设";
  }
}

function renderReport(report) {
  showView("reportView");
  document.getElementById("endingTitle").textContent = report.endingTitle;
  document.getElementById("endingSummary").textContent = report.endingSummary;
  document.getElementById("interpretation").textContent = report.interpretation;
  document.getElementById("topNeeds").textContent = report.topNeeds.join("、");
  document.getElementById("topWounds").textContent = report.topWounds.join("、");
  renderList("styleSummary", report.styleSummary);
  renderList("achievementList", report.achievements.map((id) => DATA.achievements[id]?.title || id));
}

function renderList(id, items) {
  const root = document.getElementById(id);
  root.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    root.appendChild(li);
  });
}

function renderArchive() {
  showView("archiveView");
  const archive = JSON.parse(localStorage.getItem(ARCHIVE_KEY) || "[]");
  const root = document.getElementById("archiveList");
  root.innerHTML = archive.length ? "" : "<p class='muted'>还没有保存过终局报告。</p>";
  archive.forEach((item) => {
    const card = document.createElement("div");
    card.className = "archive-card";
    card.innerHTML = `<h3>${item.endingTitle}</h3><p class="muted">${item.createdAt}</p><p>${item.endingSummary}</p><p>需求：${item.topNeeds.join("、")}</p><p>线索：${item.topWounds.join("、")}</p>`;
    root.appendChild(card);
  });
}

function renderGuide() {
  showView("guideView");
  const root = document.getElementById("guideContent");
  root.innerHTML = "";
  Object.entries(DATA.productGuide).forEach(([title, content]) => {
    const card = document.createElement("div");
    card.className = "guide-card";
    card.innerHTML = `<h3>${title}</h3><p>${content.trim().replace(/\n/g, "<br>")}</p>`;
    root.appendChild(card);
  });
}

function renderSetup() {
  renderPersonaTemplates();
  showView("setupView");
}

function renderPersonaTemplates() {
  const root = document.getElementById("personaTemplates");
  root.innerHTML = "";
  PERSONA_TEMPLATES.forEach((template) => {
    const card = document.createElement("div");
    card.className = `template-card ${template.id === selectedPersonaId ? "active" : ""}`;
    card.innerHTML = `<h3>${template.name}</h3><p>${template.desc}</p><p class="muted">${template.traits.join("、")}</p>`;
    card.addEventListener("click", () => {
      selectedPersonaId = template.id;
      document.getElementById("personaName").value = template.name;
      document.getElementById("personaCustom").value = "";
      renderPersonaTemplates();
    });
    root.appendChild(card);
  });
}

function randomizePersonaDraft() {
  const template = PERSONA_TEMPLATES[Math.floor(Math.random() * PERSONA_TEMPLATES.length)];
  selectedPersonaId = template.id;
  const variants = [
    "这一局想试着更早说出真实需要。",
    "这一局会更容易受关系波动影响，但也更愿意尝试连接。",
    "这一局表面上很能扛，内心其实很想被允许休息。",
    "这一局希望不再只用成绩、工作和表现证明自己。",
    "这一局对自由更敏感，也更容易在不确定里摇摆。",
  ];
  document.getElementById("personaName").value = template.name;
  document.getElementById("personaCustom").value = `${template.desc}${variants[Math.floor(Math.random() * variants.length)]}`;
  renderPersonaTemplates();
}

document.getElementById("startBtn").addEventListener("click", () => {
  renderSetup();
});
document.getElementById("continueBtn").addEventListener("click", () => {
  state = loadState() || createInitialState();
  renderGame();
});
document.getElementById("restartBtn").addEventListener("click", () => {
  renderSetup();
});
document.getElementById("beginWithPersonaBtn").addEventListener("click", () => {
  state = createStateFromSetup();
  currentDynamicChoices = [];
  saveState();
  renderGame();
});
document.getElementById("randomPersonaBtn").addEventListener("click", randomizePersonaDraft);
document.getElementById("aiPersonaBtn").addEventListener("click", refinePersonaWithAi);
document.getElementById("saveArchiveBtn").addEventListener("click", () => {
  if (!latestReport) return;
  const archive = JSON.parse(localStorage.getItem(ARCHIVE_KEY) || "[]");
  archive.unshift(latestReport);
  localStorage.setItem(ARCHIVE_KEY, JSON.stringify(archive));
  renderArchive();
});
document.getElementById("clearArchiveBtn").addEventListener("click", () => {
  localStorage.removeItem(ARCHIVE_KEY);
  renderArchive();
});
document.getElementById("homeBtn").addEventListener("click", () => showView("homeView"));
document.getElementById("archiveBtn").addEventListener("click", renderArchive);
document.getElementById("guideBtn").addEventListener("click", renderGuide);
document.getElementById("settingsBtn").addEventListener("click", renderAiSettings);
document.getElementById("deepseekPresetBtn").addEventListener("click", () => {
  document.getElementById("aiEndpoint").value = "https://api.deepseek.com/chat/completions";
  document.getElementById("aiModel").value = "deepseek-chat";
});
document.getElementById("saveAiSettingsBtn").addEventListener("click", saveAiSettings);
document.getElementById("clearAiSettingsBtn").addEventListener("click", () => {
  localStorage.removeItem(AI_SETTINGS_KEY);
  renderAiSettings();
});
document.getElementById("aiChoiceBtn").addEventListener("click", generateAiChoice);
document.getElementById("rerollChoicesBtn").addEventListener("click", () => {
  const node = currentNode();
  state.dynamicChoices[node.chapter] = [localDynamicChoice()];
  currentDynamicChoices = state.dynamicChoices[node.chapter];
  saveState();
  renderGame();
});

showView("homeView");
