import copy
import json
import random
import secrets
import webbrowser
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import app as core

APP_DIR = Path(__file__).parent
FULLSTACK_WEB_DIR = APP_DIR / "fullstack_web"
DATA_DIR = APP_DIR / "life_sim_data"
DATA_DIR.mkdir(exist_ok=True)
AI_CONFIG_FILE = DATA_DIR / "ai_config.json"


PERSONA_TEMPLATES = [
    {
        "id": "careful_achiever",
        "name": "谨慎的好学生",
        "desc": "习惯提前准备，害怕出错，容易把结果和价值感绑在一起。",
        "traits": ["谨慎", "高标准", "怕否定"],
        "effects": {
            "resources": {"career": 5, "energy": -3, "stability": -2},
            "wounds": {"worth": 5, "control": 3},
            "needs": {"achievement": 4, "safety": 3},
            "styles": {"reflect": 2, "selfBlame": 1},
            "tags": ["persona_achiever"],
        },
    },
    {
        "id": "quiet_observer",
        "name": "安静的观察者",
        "desc": "很会察言观色，不轻易表达真实需要，关系里的细微变化会被放大。",
        "traits": ["敏感", "克制", "怕打扰"],
        "effects": {
            "resources": {"relationship": 2, "stability": -2},
            "wounds": {"abandonment": 4, "neglect": 4},
            "needs": {"seen": 4, "belonging": 3},
            "styles": {"avoid": 2, "solo": 1},
            "tags": ["persona_observer"],
        },
    },
    {
        "id": "warm_connector",
        "name": "温暖的连接者",
        "desc": "重视关系和回应，愿意靠近别人，也容易为了维持气氛委屈自己。",
        "traits": ["重情感", "会照顾人", "怕失去"],
        "effects": {
            "resources": {"relationship": 6, "energy": -2},
            "wounds": {"abandonment": 3, "overload": 2},
            "needs": {"belonging": 5, "seen": 3},
            "styles": {"please": 2, "seekHelp": 1},
            "tags": ["persona_connector"],
        },
    },
    {
        "id": "restless_explorer",
        "name": "不安分的探索者",
        "desc": "更在意自由和可能性，能接受不确定，也更容易被波动消耗。",
        "traits": ["自主", "好奇", "不耐束缚"],
        "effects": {
            "resources": {"career": 2, "stability": -4, "energy": 2},
            "wounds": {"control": 3, "rejection": 2},
            "needs": {"autonomy": 6, "achievement": 2},
            "styles": {"self": 2, "face": 1},
            "tags": ["persona_explorer"],
        },
    },
    {
        "id": "tired_responsible",
        "name": "早熟的承担者",
        "desc": "很早学会懂事和补位，可靠，但不太知道什么时候可以停下来。",
        "traits": ["负责", "能扛", "容易透支"],
        "effects": {
            "resources": {"career": 3, "energy": -6, "relationship": 2},
            "wounds": {"overload": 6, "neglect": 2},
            "needs": {"recovery": 5, "safety": 2},
            "styles": {"solo": 2, "please": 1},
            "tags": ["persona_responsible"],
        },
    },
    {
        "id": "self_rebuilder",
        "name": "正在重建的人",
        "desc": "已经隐约意识到旧模式存在，希望这一局更早看见自己。",
        "traits": ["反思", "修复", "边界"],
        "effects": {
            "resources": {"stability": 4, "energy": 2},
            "wounds": {"worth": -2, "overload": -1},
            "needs": {"autonomy": 4, "recovery": 4, "seen": 2},
            "styles": {"reflect": 2, "flexible": 2},
            "tags": ["persona_rebuilder"],
        },
    },
]

RANDOM_EVENTS = [
    {
        "title": "今天特别想被肯定",
        "desc": "你比平时更在意别人的语气，哪怕一句普通评价也容易在心里停很久。",
        "weightTags": ["early_shame", "rank_internalized", "persona_achiever"],
        "effects": {"wounds": {"worth": 2, "rejection": 1}, "needs": {"seen": 2}},
    },
    {
        "title": "身体先替你喊了停",
        "desc": "你没有明显崩溃，只是突然很累，连回复消息都像要从很远的地方把自己拽回来。",
        "weightTags": ["keep_carrying", "persona_responsible", "after_hours_compliance"],
        "effects": {"resources": {"energy": -4, "stability": -1}, "needs": {"recovery": 3}},
    },
    {
        "title": "有人给了你意外的善意",
        "desc": "一个并不隆重的回应，让你短暂地感觉自己没有那么孤单。",
        "weightTags": ["child_reached_peer", "rank_shared", "persona_connector"],
        "effects": {"resources": {"relationship": 3, "stability": 2}, "needs": {"belonging": 2}},
    },
    {
        "title": "你突然很想自己做主",
        "desc": "不是为了反抗谁，而是某个瞬间你清楚地知道：这件事不能再只按别人的期待来。",
        "weightTags": ["persona_explorer", "child_asked_chance", "boundary_stated"],
        "effects": {"needs": {"autonomy": 3}, "styles": {"self": 1}},
    },
    {
        "title": "旧记忆轻轻冒头",
        "desc": "眼前的场景让你想起更早以前的某个时刻，你没有完全被拉回去，但心里确实颤了一下。",
        "weightTags": ["child_hidden_mistake", "child_unpicked_memory", "early_surface_peace"],
        "effects": {"wounds": {"abandonment": 1, "neglect": 1, "worth": 1}, "needs": {"safety": 2}},
    },
]

LOCAL_DYNAMIC_CHOICES = [
    {
        "text": "先不急着选，写下一句此刻最真实的感受。",
        "effects": {"resources": {"stability": 3}, "needs": {"seen": 2, "recovery": 1}, "styles": {"reflect": 2}, "tags": ["dynamic_self_note"]},
    },
    {
        "text": "问问自己：这个选择是在保护我，还是在惩罚我？",
        "effects": {"resources": {"stability": 4}, "wounds": {"worth": -1}, "needs": {"autonomy": 2}, "styles": {"flexible": 2, "reflect": 1}, "tags": ["dynamic_pattern_check"]},
    },
    {
        "text": "给一个可信的人发出很短的求助信号。",
        "effects": {"resources": {"relationship": 3, "stability": 2}, "needs": {"belonging": 2, "seen": 2}, "styles": {"seekHelp": 2}, "tags": ["dynamic_reach_out"]},
    },
    {
        "text": "允许自己选一个不那么完美、但更能呼吸的方案。",
        "effects": {"resources": {"energy": 3, "stability": 2, "career": -1}, "needs": {"recovery": 3, "autonomy": 2}, "styles": {"flexible": 2, "self": 1}, "tags": ["dynamic_breathable_choice"]},
    },
]

sessions: dict[str, dict[str, Any]] = {}


class PersonaPayload(BaseModel):
    template_id: str = "careful_achiever"
    name: str | None = None
    custom: str | None = None
    random_level: str = Field(default="medium", pattern="^(low|medium|high)$")


class ChoicePayload(BaseModel):
    choice_index: int


class AIConfigPayload(BaseModel):
    provider: str = "deepseek"
    endpoint: str = "https://api.deepseek.com/chat/completions"
    model: str = "deepseek-chat"
    api_key: str


class PersonaRefinePayload(BaseModel):
    template_id: str = "careful_achiever"
    name: str | None = None
    custom: str | None = None


def apply_effects(state: dict[str, Any], effects: dict[str, Any]) -> None:
    for k, v in effects.get("resources", {}).items():
        state["resources"][k] = core.clamp(state["resources"].get(k, 0) + v)
    for k, v in effects.get("wounds", {}).items():
        state["wounds"][k] = core.clamp(state["wounds"].get(k, 0) + v)
    for k, v in effects.get("needs", {}).items():
        state["needs"][k] = core.clamp(state["needs"].get(k, 0) + v, 0, 999)
    for k, v in effects.get("styles", {}).items():
        state["styles"][k] = state["styles"].get(k, 0) + v
    state["tags"].extend(effects.get("tags", []))


def template_by_id(template_id: str) -> dict[str, Any]:
    return next((item for item in PERSONA_TEMPLATES if item["id"] == template_id), PERSONA_TEMPLATES[0])


def random_chance(level: str) -> float:
    return {"low": 0.25, "medium": 0.48, "high": 0.75}.get(level, 0.48)


def ensure_random_event(session: dict[str, Any]) -> dict[str, Any] | None:
    state = session["state"]
    node = core.STORY_NODES[state["nodeIndex"]]
    chapter = str(node["chapter"])
    if chapter in state["randomEvents"]:
        return state["randomEvents"][chapter]

    rng = session["rng"]
    if rng.random() > random_chance(state["randomLevel"]):
        state["randomEvents"][chapter] = None
        return None

    tags = set(state["tags"])
    pool = []
    for event in RANDOM_EVENTS:
        weight = 1 + len([tag for tag in event.get("weightTags", []) if tag in tags]) * 2
        pool.extend([event] * weight)
    event = copy.deepcopy(rng.choice(pool))
    state["randomEvents"][chapter] = event
    apply_effects(state, event.get("effects", {}))
    return event


def ensure_dynamic_choices(session: dict[str, Any]) -> list[dict[str, Any]]:
    state = session["state"]
    node = core.STORY_NODES[state["nodeIndex"]]
    chapter = str(node["chapter"])
    if chapter not in state["dynamicChoices"]:
        state["dynamicChoices"][chapter] = []
        if session["rng"].random() < random_chance(state["randomLevel"]):
            choice = copy.deepcopy(session["rng"].choice(LOCAL_DYNAMIC_CHOICES))
            choice["source"] = "local_dynamic"
            state["dynamicChoices"][chapter].append(choice)
    return state["dynamicChoices"][chapter]


def available_choices(session: dict[str, Any]) -> list[dict[str, Any]]:
    state = session["state"]
    node = core.STORY_NODES[state["nodeIndex"]]
    story_choices = [
        {"index": idx, "source": "story", **choice}
        for idx, choice in core.get_available_choices(node, state)
    ]
    dynamic_choices = [
        {"index": 1000 + idx, "source": choice.get("source", "local_dynamic"), **choice}
        for idx, choice in enumerate(ensure_dynamic_choices(session))
    ]
    choices = story_choices + dynamic_choices
    if session["rng"].random() < {"low": 0.15, "medium": 0.55, "high": 1.0}.get(state["randomLevel"], 0.55):
        session["rng"].shuffle(choices)
    return choices


def public_state(session_id: str) -> dict[str, Any]:
    session = sessions[session_id]
    state = session["state"]
    if state["finished"]:
        return {"session_id": session_id, "finished": True, "report": core.build_final_report(state)}
    event = ensure_random_event(session)
    node = core.STORY_NODES[state["nodeIndex"]]
    return {
        "session_id": session_id,
        "finished": False,
        "persona": state.get("persona"),
        "node": node,
        "choices": available_choices(session),
        "state": state,
        "random_event": event,
        "labels": core.LABELS,
        "story_count": len(core.STORY_NODES),
    }


def save_ai_config(config: dict[str, Any]) -> None:
    AI_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def load_ai_config() -> dict[str, Any] | None:
    if not AI_CONFIG_FILE.exists():
        return None
    try:
        return json.loads(AI_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


async def call_llm(prompt: str, temperature: float = 0.8) -> dict[str, Any]:
    config = load_ai_config()
    if not config:
        raise HTTPException(status_code=400, detail="未配置 AI。请先在设置页保存 DeepSeek 或 OpenAI 兼容接口。")
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                config["endpoint"],
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config['api_key']}",
                },
                json={
                    "model": config["model"],
                    "messages": [
                        {"role": "system", "content": "你只输出严格 JSON，不输出 Markdown，不输出解释。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                },
            )
        if response.status_code == 402:
            raise HTTPException(status_code=402, detail="AI API 余额不足，请充值或更换 Key。")
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(raw)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI 调用失败：{exc}") from exc


api = FastAPI(title="命运回响本地前后端版")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8787", "http://localhost:8787"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    return {
        "personas": PERSONA_TEMPLATES,
        "labels": core.LABELS,
        "endings": core.ENDING_DICTIONARY,
        "achievements": core.ACHIEVEMENTS_DICTIONARY,
        "ai_configured": load_ai_config() is not None,
    }


@api.post("/api/ai/config")
def configure_ai(payload: AIConfigPayload) -> dict[str, Any]:
    config = payload.model_dump()
    save_ai_config(config)
    return {
        "configured": True,
        "provider": config["provider"],
        "endpoint": config["endpoint"],
        "model": config["model"],
    }


@api.delete("/api/ai/config")
def clear_ai() -> dict[str, bool]:
    if AI_CONFIG_FILE.exists():
        AI_CONFIG_FILE.unlink()
    return {"configured": False}


@api.post("/api/persona/refine")
async def refine_persona(payload: PersonaRefinePayload) -> dict[str, Any]:
    template = template_by_id(payload.template_id)
    prompt = "\n".join([
        "请为一个现实人生模拟游戏生成开局人设。",
        "要求：温和、具体、有可玩性；不要诊断；不要使用病理标签；不要超过120字。",
        "只输出 JSON：{\"name\":\"...\",\"desc\":\"...\",\"traits\":[\"...\",\"...\",\"...\"]}",
        f"基础模板：{template['name']}｜{template['desc']}",
        f"用户输入名字：{payload.name or template['name']}",
        f"用户补充：{payload.custom or '无'}",
    ])
    return await call_llm(prompt, temperature=0.85)


@api.post("/api/session/start")
def start_session(payload: PersonaPayload) -> dict[str, Any]:
    template = template_by_id(payload.template_id)
    state = core.create_initial_state()
    state["seed"] = random.randint(1, 10**9)
    state["randomLevel"] = payload.random_level
    state["randomEvents"] = {}
    state["dynamicChoices"] = {}
    state["persona"] = {
        "id": template["id"],
        "name": payload.name or template["name"],
        "baseName": template["name"],
        "desc": payload.custom or template["desc"],
        "traits": template["traits"],
        "custom": payload.custom or "",
    }
    apply_effects(state, template["effects"])
    if payload.custom:
        state["tags"].append("persona_custom")
        state["needs"]["seen"] += 2
        state["styles"]["reflect"] += 1

    session_id = secrets.token_urlsafe(12)
    sessions[session_id] = {"state": state, "rng": random.Random(state["seed"])}
    return public_state(session_id)


@api.get("/api/session/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已重启丢失，请重新开始。")
    return public_state(session_id)


@api.post("/api/session/{session_id}/choice")
def submit_choice(session_id: str, payload: ChoicePayload) -> dict[str, Any]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已重启丢失，请重新开始。")
    session = sessions[session_id]
    state = session["state"]
    if state["finished"]:
        return public_state(session_id)
    node = core.STORY_NODES[state["nodeIndex"]]
    choice_map = {choice["index"]: choice for choice in available_choices(session)}
    choice = choice_map.get(payload.choice_index)
    if not choice:
        raise HTTPException(status_code=400, detail="当前选项不可用。")
    state["dynamicChoices"].pop(str(node["chapter"]), None)
    next_state = core.apply_choice(state, node, choice, payload.choice_index)
    session["state"] = next_state
    return public_state(session_id)


@api.post("/api/session/{session_id}/ai-choice")
async def generate_ai_choice(session_id: str) -> dict[str, Any]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已重启丢失，请重新开始。")
    session = sessions[session_id]
    state = session["state"]
    node = core.STORY_NODES[state["nodeIndex"]]
    prompt = "\n".join([
        "你是互动叙事游戏的选项生成器。",
        "请基于用户人设、当前人生节点和状态，生成一个新的可选行动。",
        "要求：中文，40字以内，像游戏按钮；不要说教；不要诊断；不要输出解释。",
        "只输出 JSON：{\"text\":\"...\"}",
        f"人设：{json.dumps(state.get('persona'), ensure_ascii=False)}",
        f"当前节点：{node['title']}｜{node['scene']}",
        f"资源：{json.dumps(state['resources'], ensure_ascii=False)}",
        f"需求：{json.dumps(state['needs'], ensure_ascii=False)}",
        f"受伤线索：{json.dumps(state['wounds'], ensure_ascii=False)}",
    ])
    parsed = await call_llm(prompt, temperature=0.9)
    choice = {
        "text": parsed.get("text") or "按此刻更真实的需要做一个小决定。",
        "source": "ai",
        "effects": {
            "resources": {"stability": 2},
            "needs": {"seen": 2, "autonomy": 1},
            "styles": {"reflect": 1, "face": 1},
            "tags": ["ai_dynamic_choice"],
        },
    }
    chapter = str(node["chapter"])
    state["dynamicChoices"].setdefault(chapter, []).append(choice)
    return public_state(session_id)


if FULLSTACK_WEB_DIR.exists():
    api.mount("/", StaticFiles(directory=FULLSTACK_WEB_DIR, html=True), name="web")


def open_browser() -> None:
    webbrowser.open("http://127.0.0.1:8787")


if __name__ == "__main__":
    import uvicorn

    open_browser()
    uvicorn.run("api_server:api", host="127.0.0.1", port=8787, reload=False)
