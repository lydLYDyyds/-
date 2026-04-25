const DATA = window.LIFE_ECHO_DATA;
const STORAGE_KEY = "life_echo_web_state";
const ARCHIVE_KEY = "life_echo_web_archive";

let state = loadState() || createInitialState();
let latestReport = null;

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

function currentNode() {
  return DATA.storyNodes[state.nodeIndex];
}

function applyChoice(choice, choiceIndex) {
  const node = currentNode();
  const effects = choice.effects || {};
  Object.entries(effects.resources || {}).forEach(([key, value]) => {
    state.resources[key] = clamp((state.resources[key] || 0) + value);
  });
  Object.entries(effects.wounds || {}).forEach(([key, value]) => {
    state.wounds[key] = clamp((state.wounds[key] || 0) + value);
  });
  Object.entries(effects.needs || {}).forEach(([key, value]) => {
    state.needs[key] = clamp((state.needs[key] || 0) + value, 0, 999);
  });
  Object.entries(effects.styles || {}).forEach(([key, value]) => {
    state.styles[key] = (state.styles[key] || 0) + value;
  });
  state.tags.push(...(effects.tags || []));
  state.choices.push({
    nodeId: node.id,
    nodeTitle: node.title,
    choiceIndex,
    choiceText: choice.text,
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
  showView("gameView");
  document.getElementById("chapterLabel").textContent = `第 ${node.chapter} 章 · ${state.startedAt}`;
  document.getElementById("nodeTitle").textContent = node.title;
  document.getElementById("nodeScene").textContent = node.scene;
  document.getElementById("nodeAnchor").textContent = node.anchor;
  const previous = state.chapterSummaries.find((item) => item.chapter === node.chapter - 1);
  const mirror = document.getElementById("previousMirror");
  mirror.classList.toggle("hidden", !previous);
  mirror.textContent = previous ? `${previous.title}：${previous.content}` : "";

  const choices = document.getElementById("choices");
  choices.innerHTML = "";
  node.choices.forEach((choice, index) => {
    if (!choiceIsAvailable(choice)) return;
    const button = document.createElement("button");
    button.className = "choice";
    button.textContent = choice.text;
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
  renderBars("resources", state.resources, DATA.labels.resources, 100);
  renderBars("needs", state.needs, DATA.labels.needs, 20);
  renderStoryMap();
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

document.getElementById("startBtn").addEventListener("click", () => {
  state = createInitialState();
  saveState();
  renderGame();
});
document.getElementById("continueBtn").addEventListener("click", () => {
  state = loadState() || createInitialState();
  renderGame();
});
document.getElementById("restartBtn").addEventListener("click", () => {
  state = createInitialState();
  saveState();
  renderGame();
});
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

showView("homeView");
