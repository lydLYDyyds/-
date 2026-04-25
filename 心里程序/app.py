
import json
import copy
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent


def resolve_save_dir() -> Path:
    candidates = [
        APP_DIR / "life_sim_data",
        Path.home() / ".life_sim_data",
    ]
    for candidate in candidates:
        try:
            candidate.mkdir(exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError("无法创建存档目录，请检查当前用户的文件写入权限。")


SAVE_DIR = resolve_save_dir()

CURRENT_SAVE_FILE = SAVE_DIR / "current_save.json"
ARCHIVE_FILE = SAVE_DIR / "archive.json"
ACHIEVEMENTS_FILE = SAVE_DIR / "achievements.json"


LABELS = {
    "resources": {
        "career": "学业/事业进度",
        "money": "金钱",
        "energy": "精力",
        "relationship": "关系温度",
        "stability": "内在稳定度",
    },
    "wounds": {
        "rejection": "否定敏感",
        "abandonment": "遗弃敏感",
        "control": "失控恐惧",
        "overload": "责任过载",
        "neglect": "情感忽视痕迹",
        "worth": "价值感脆弱",
    },
    "needs": {
        "safety": "安全感",
        "seen": "被看见",
        "control": "掌控感",
        "belonging": "归属与连接",
        "autonomy": "自主与边界",
        "achievement": "成就与价值确认",
        "recovery": "休息与修复",
    },
    "styles": {
        "face": "面对问题",
        "avoid": "回避不适",
        "self": "坚持自我",
        "please": "优先取悦",
        "seekHelp": "主动求助",
        "solo": "独自承担",
        "reflect": "深思权衡",
        "impulse": "即时补偿",
        "flexible": "弹性解释",
        "selfBlame": "自我苛责",
    },
}

ENDING_DICTIONARY = {
    "hollow_success": {
        "title": "体面而空心的人生",
        "summary": "你把很多选择都做得足够正确、足够稳妥，外部轨迹并不难看，但真正属于你的那部分声音被压得很低。你并非没有能力，而是长期把“不能出错”放在了“我想要什么”之前。",
    },
    "free_but_unstable": {
        "title": "自由胜过安全",
        "summary": "你没有一直按安全答案行走。你承受了更多波动，也因此更频繁地直面自己的欲望与边界。代价是稳定度反复受冲击，但你至少没有把自己完全交给别人的剧本。",
    },
    "everyone_happy_except_you": {
        "title": "所有人都满意，只有你没有",
        "summary": "你很擅长照顾局面、维持体面、消化冲突。只是很多让事情顺利的选择，代价是你一次次把自己的真实需要排到后面。问题不在于你不够懂事，而在于你太习惯先顾全局。",
    },
    "delayed_bloom": {
        "title": "晚熟型开花",
        "summary": "你的人生前段并不顺滑，甚至绕了不少路，但你没有完全停在旧模式里。你开始学会用自己的节奏活，而不是用别人的评价系统活。",
    },
    "exhausted_survivor": {
        "title": "一直扛到快没有力气",
        "summary": "你最擅长的是撑住。很多局面之所以没有塌，是因为你一直在补位、扛责、维持运转。但“能扛”并不代表“不累”，你当前最缺的，可能不是新的目标，而是被允许恢复。",
    },
    "connected_and_warm": {
        "title": "关系丰盈的人生",
        "summary": "你没有把所有筹码都押在绩效、产出或胜负上。你在一些关键节点里选择了连接、回应和在场，因此并不一定拥有最高的外部指标，却更少出现彻底失联的时刻。",
    },
    "integrated_self": {
        "title": "把人生慢慢还给自己",
        "summary": "你没有把旧模式一次性清空，但你开始能分辨：哪些是现实责任，哪些是早年形成的自动反应。你仍会在意结果和关系，却不再愿意把自己完全交给恐惧、期待或证明欲来管理。",
    },
    "quiet_repair": {
        "title": "安静修复中的人生",
        "summary": "你没有突然变得轻松，也没有立刻找到完美答案。但你开始把恢复、求助、边界和真实表达放进生活里。它们看起来不如胜利耀眼，却让你逐渐拥有更能承接自己的日子。",
    },
}

ACHIEVEMENTS_DICTIONARY = {
    "first_step": {"id": "first_step", "title": "开始存档", "desc": "完成第一章。"},
    "no_one_bothered": {"id": "no_one_bothered", "title": "不肯麻烦别人", "desc": "整局几乎从不主动求助。"},
    "chose_self_once": {"id": "chose_self_once", "title": "终于替自己选了一次", "desc": "在关键节点明确优先了自己的边界。"},
    "hold_everything": {"id": "hold_everything", "title": "把稳妥活成了习惯", "desc": "多数关键节点都优先选择安全。"},
    "freedom_over_safety": {"id": "freedom_over_safety", "title": "自由胜过安全", "desc": "在多次高风险节点优先了自主性。"},
    "still_standing": {"id": "still_standing", "title": "一直扛到最后", "desc": "精力长期较低，但仍完成全程。"},
    "soft_connection": {"id": "soft_connection", "title": "有人在你的生命里留下了痕迹", "desc": "关系温度保持较高。"},
    "hidden_branch_hollow": {"id": "hidden_branch_hollow", "title": "你差一点忘了自己", "desc": "触发隐藏结局：体面而空心的人生。"},
    "pattern_seen": {"id": "pattern_seen", "title": "我看见了重复发生的事", "desc": "在后期章节中主动识别旧模式。"},
    "asked_clearly": {"id": "asked_clearly", "title": "把需要说清楚", "desc": "在关系里直接表达需求，而不是只靠猜测。"},
    "repair_begins": {"id": "repair_begins", "title": "修复从这里开始", "desc": "选择停止自动透支，开始认真照顾自己。"},
    "return_to_self": {"id": "return_to_self", "title": "回到自己这边", "desc": "在终章里不再只用外界标准解释自己。"},
}

PRODUCT_GUIDE = {
    "快速开始": """
1. 点击“新的人生”开始一局完整体验。
2. 每一章只需要按当下最真实的反应选择，不需要追求最优解。
3. 右侧会显示资源、需求趋势和剧情树路径，它们会随着选择变化。
4. 完成终章后会生成终局报告，并自动保存到档案馆。
5. 多玩几局后，可以在“平行人生对照”里比较不同路线的差异。
    """,
    "指标说明": """
- 资源：描述当下可用的外部与内部条件，例如学业/事业、精力、关系温度和内在稳定度。
- 受伤线索：描述剧情选择中被反复触发的敏感点，例如否定、遗弃、失控、过载、忽视和价值感。
- 当前需求：描述你在这条路径里越来越需要什么，例如安全感、被看见、掌控感、归属、自主、成就或修复。
- 决策风格：记录你更常用的应对方式，例如面对、回避、取悦、求助、独自承担、反思或自责。
- 隐藏标签：不会逐条解释给用户看，但会影响后续条件分支、成就和结局。
    """,
    "适用边界": """
这个产品适合用于自我觉察、互动叙事、心理主题原型演示、团体工作坊中的非临床讨论。
它不适合替代心理咨询、医学诊断、危机干预或对现实关系做单次判断。
如果体验过程中出现强烈不适、持续失眠、自伤想法或现实安全风险，应暂停使用并寻求现实中的专业支持。
    """,
    "模块复用": """
作为程序使用：运行 streamlit run app.py。
作为模块使用：import life_echo 后调用 create_initial_state、get_current_node、get_available_choices、choose、simulate_life、build_final_report。
数据默认保存在项目目录 life_sim_data 中；如果目录不可写，会自动退到用户目录 .life_sim_data。
    """,
}

STORY_NODES = [
    {
        "id": "primary_school_window",
        "chapter": 1,
        "title": "小学午后的窗边座位",
        "scene": "下午的光斜斜落在教室地砖上，粉笔灰悬在空气里，像一层很轻的雾。老师让大家把听写本从后往前传，你听见纸页翻动的声音越来越近。你的本子上有两个红圈，圈得不重，却像钉子一样钉在眼前。前排同学回头看了一眼，笑了一下，你分不清那是不是在笑你。你忽然很想把本子压到桌洞最深处。",
        "anchor": "【现实锚点】蓝色塑料桌椅、听写本上的红圈、下课铃响前越来越长的三分钟。",
        "choices": [
            {
                "text": "把本子藏起来，装作没事，放学再偷偷改。",
                "effects": {
                    "resources": {"stability": -3, "energy": -2},
                    "wounds": {"rejection": 5, "worth": 4, "neglect": 2},
                    "needs": {"safety": 5, "seen": 3},
                    "styles": {"avoid": 2, "selfBlame": 2, "solo": 1},
                    "tags": ["child_hidden_mistake", "early_shame"],
                },
            },
            {
                "text": "举手问老师：我想知道这两个字错在哪里。",
                "effects": {
                    "resources": {"career": 3, "stability": 3},
                    "wounds": {"rejection": 1, "worth": -1},
                    "needs": {"control": 4, "seen": 4, "achievement": 2},
                    "styles": {"face": 2, "seekHelp": 1, "reflect": 1},
                    "tags": ["child_asked_teacher"],
                },
            },
            {
                "text": "看向同桌，轻声问：你能不能也给我看一下你的？",
                "effects": {
                    "resources": {"relationship": 4, "stability": 2},
                    "wounds": {"abandonment": 1, "worth": 1},
                    "needs": {"belonging": 5, "seen": 4},
                    "styles": {"seekHelp": 2, "face": 1},
                    "tags": ["child_reached_peer"],
                },
            },
        ],
    },
    {
        "id": "primary_school_performance",
        "chapter": 2,
        "title": "被选中和没被选中的那天",
        "scene": "学校要排节目，班主任站在讲台前点名字。被叫到的人从座位上站起来，椅脚划过地面，声音又短又亮。你一直盯着老师手里的名单，直到她把纸折起来，说“其他同学负责后勤”。那一刻你说不上是轻松还是失落，只觉得胸口像被塞进一团没拆开的纸。",
        "anchor": "【现实锚点】礼堂后台的红绒幕布、名单上没有出现的名字、同学换演出服时的笑声。",
        "choices": [
            {
                "text": "告诉自己后勤也很重要，把东西准备得没有一点差错。",
                "effects": {
                    "resources": {"career": 3, "relationship": 2, "energy": -3},
                    "wounds": {"overload": 4, "worth": 3},
                    "needs": {"achievement": 4, "belonging": 3},
                    "styles": {"please": 2, "solo": 1, "selfBlame": 1},
                    "tags": ["child_useful_role"],
                },
            },
            {
                "text": "主动问老师：下次我能不能试一次？",
                "effects": {
                    "resources": {"stability": 3, "career": 2},
                    "wounds": {"rejection": 2, "control": 1},
                    "needs": {"seen": 5, "autonomy": 4, "achievement": 3},
                    "styles": {"face": 2, "self": 2},
                    "tags": ["child_asked_chance"],
                },
            },
            {
                "text": "悄悄远离那群被选中的人，假装自己本来就不想去。",
                "effects": {
                    "resources": {"relationship": -2, "stability": -2},
                    "wounds": {"abandonment": 4, "neglect": 4, "worth": 2},
                    "needs": {"safety": 4, "seen": 4},
                    "styles": {"avoid": 2, "solo": 2},
                    "tags": ["child_unpicked_memory"],
                },
            },
        ],
    },
    {
        "id": "middle_school_rank",
        "chapter": 3,
        "title": "初中月考排名贴在墙上",
        "scene": "走廊尽头的公告栏被围得水泄不通，玻璃上贴着一张新打印的排名表。有人挤进去，有人故意大声念出自己的名次。你站在人群外，听见自己的心跳和楼梯间的回声混在一起。纸上每一个名字都那么整齐，像一排排被钉住的位置，而你要在里面找到自己。",
        "anchor": "【现实锚点】公告栏玻璃上的指纹、红色排名数字、课间十分钟里突然变轻或变重的空气。",
        "choices": [
            {
                "text": "盯着排名，把它记下来，晚上重新规划所有时间。",
                "effects": {
                    "resources": {"career": 6, "energy": -5, "stability": -4},
                    "wounds": {"worth": 5, "control": 4, "rejection": 3},
                    "needs": {"achievement": 6, "control": 4},
                    "styles": {"face": 2, "selfBlame": 2, "reflect": 1},
                    "tags": ["rank_internalized", "early_performance_pressure"],
                },
            },
            {
                "text": "先离开公告栏，等人散了再看，别让自己被围观吞掉。",
                "effects": {
                    "resources": {"stability": 4, "energy": 2},
                    "wounds": {"control": 1, "rejection": 1},
                    "needs": {"safety": 5, "recovery": 3},
                    "styles": {"reflect": 2, "flexible": 1},
                    "tags": ["rank_self_protected"],
                },
            },
            {
                "text": "找朋友一起看，至少不用一个人面对那张纸。",
                "effects": {
                    "resources": {"relationship": 5, "stability": 3},
                    "wounds": {"abandonment": 1, "worth": 2},
                    "needs": {"belonging": 5, "seen": 4},
                    "styles": {"seekHelp": 2, "face": 1},
                    "tags": ["rank_shared"],
                },
            },
        ],
    },
    {
        "id": "middle_school_friend_circle",
        "chapter": 4,
        "title": "初中朋友之间的站队",
        "scene": "午休时，教室后排有人压低声音说话。你经过时，那几个人忽然停了下来，又很快换成别的话题。你知道也许这只是巧合，可那种被排除在外的感觉来得太快，像冷水顺着后背滑下去。你想问，又怕一问就证明自己在意。",
        "anchor": "【现实锚点】半拉上的窗帘、课桌里没吃完的面包、被突然合上的聊天窗口。",
        "choices": [
            {
                "text": "装作不知道，继续和大家保持差不多的距离。",
                "effects": {
                    "resources": {"relationship": 1, "stability": -3},
                    "wounds": {"abandonment": 5, "neglect": 3},
                    "needs": {"belonging": 5, "safety": 3},
                    "styles": {"avoid": 2, "please": 2, "solo": 1},
                    "tags": ["early_surface_peace"],
                },
            },
            {
                "text": "挑一个最信任的人问清楚：是不是我误会了？",
                "effects": {
                    "resources": {"relationship": 4, "stability": 3},
                    "wounds": {"abandonment": 2, "rejection": 1},
                    "needs": {"seen": 5, "belonging": 4, "control": 2},
                    "styles": {"face": 2, "seekHelp": 2},
                    "tags": ["early_clarified_relation"],
                },
            },
            {
                "text": "把注意力转回学习，至少成绩不会突然不理你。",
                "effects": {
                    "resources": {"career": 5, "relationship": -3, "energy": -3},
                    "wounds": {"neglect": 4, "worth": 3, "overload": 2},
                    "needs": {"achievement": 5, "safety": 3},
                    "styles": {"avoid": 1, "solo": 2, "selfBlame": 1},
                    "tags": ["achievement_as_shelter"],
                },
            },
        ],
    },
    {
        "id": "gaokao_night",
        "chapter": 1,
        "title": "高考前夜",
        "scene": "夜里 11:47，台灯把试卷边缘照得发白。桌上摊着一页数学压轴题，手机不断弹出同学们的消息：‘你们还在刷题吗？’‘我感觉我完了。’客厅里，家人已经轻声走动，刻意不制造声音。你知道自己应该睡，可脑子里一直在响：如果明天没发挥好，会怎样？",
        "anchor": "【现实锚点】高考倒计时：00天；草稿纸上写满没来得及擦掉的步骤。",
        "choices": [
            {
                "text": "再做 20 分钟，把最后一道题硬啃完。",
                "effects": {
                    "resources": {"career": 8, "energy": -10, "stability": -6},
                    "wounds": {"rejection": 8, "worth": 6, "control": 4},
                    "needs": {"achievement": 8, "safety": 4},
                    "styles": {"face": 2, "selfBlame": 2, "reflect": 1},
                    "tags": ["high_pressure", "exam_memory"],
                },
            },
            {
                "text": "把题合上，告诉自己先睡，明天至少保证状态。",
                "effects": {
                    "resources": {"energy": 8, "stability": 6, "career": 2},
                    "wounds": {"control": 2},
                    "needs": {"recovery": 8, "safety": 3},
                    "styles": {"face": 1, "flexible": 2, "reflect": 1},
                    "tags": ["self_regulation"],
                },
            },
            {
                "text": "给最信任的人发一句：‘我有点慌。’",
                "effects": {
                    "resources": {"relationship": 7, "stability": 5, "energy": 2},
                    "wounds": {"abandonment": 3, "worth": 2},
                    "needs": {"seen": 8, "belonging": 6},
                    "styles": {"seekHelp": 3, "face": 1},
                    "tags": ["support_reached"],
                },
            },
        ],
    },
    {
        "id": "score_and_choice",
        "chapter": 2,
        "title": "查分与志愿",
        "scene": "分数出来了，不算失常，也不算理想。你盯着几所学校和专业，浏览器标签页开了一排。父母更希望你选稳定、就业明确的方向；你自己却被另一个城市、另一个专业吸引。你知道这次决定很难回头。",
        "anchor": "【现实锚点】志愿表格、城市名、专业代码、家人沉默后的那句‘你自己想清楚’。",
        "choices": [
            {
                "text": "选更稳、更被家里认可的专业和城市。",
                "effects": {
                    "resources": {"stability": 6, "money": 3, "career": 4, "relationship": 4},
                    "wounds": {"overload": 4, "neglect": 3},
                    "needs": {"safety": 8, "belonging": 4},
                    "styles": {"please": 3, "reflect": 2},
                    "tags": ["safe_path", "family_approved"],
                },
            },
            {
                "text": "选自己更想读的方向，即使不那么稳。",
                "effects": {
                    "resources": {"career": 5, "stability": -2, "relationship": -3},
                    "wounds": {"rejection": 3, "control": 2},
                    "needs": {"autonomy": 9, "achievement": 4},
                    "styles": {"self": 3, "face": 2},
                    "tags": ["autonomy_path", "city_change"],
                },
            },
            {
                "text": "先选一个折中方案：专业保守一些，但争取更想去的城市。",
                "effects": {
                    "resources": {"stability": 3, "career": 3, "relationship": 1},
                    "wounds": {"control": 3},
                    "needs": {"safety": 4, "autonomy": 4},
                    "styles": {"reflect": 3, "face": 1},
                    "tags": ["compromise_path"],
                },
            },
        ],
    },
    {
        "id": "freshman_room",
        "chapter": 3,
        "title": "大学宿舍与新的人际秩序",
        "scene": "军训结束后，关系还没真正稳定。有人外向、有人安静；有人似乎很快就找到圈子，而你开始意识到自己并不总是能轻松融进去。某天夜里，有室友在群里阴阳怪气，似乎影射的是你。",
        "anchor": "【现实锚点】熄灯后的宿舍群消息、阳台风声、‘你是不是想太多了’这句话。",
        "choices": [
            {
                "text": "装作没看见，维持表面平稳。",
                "effects": {
                    "resources": {"stability": -4, "relationship": 1},
                    "wounds": {"abandonment": 5, "neglect": 4},
                    "needs": {"safety": 4, "belonging": 5},
                    "styles": {"avoid": 3, "please": 2, "solo": 1},
                    "tags": ["surface_peace"],
                },
            },
            {
                "text": "私下问清楚，尽量不把局面闹大。",
                "effects": {
                    "resources": {"relationship": 3, "stability": 2},
                    "wounds": {"rejection": 2, "control": 2},
                    "needs": {"seen": 4, "control": 3},
                    "styles": {"face": 2, "reflect": 2},
                    "tags": ["clarify_privately"],
                },
            },
            {
                "text": "明确表达边界：如果有问题就直接说，不要影射。",
                "effects": {
                    "resources": {"stability": 4, "relationship": -2},
                    "wounds": {"control": 1},
                    "needs": {"autonomy": 7, "seen": 3},
                    "styles": {"self": 3, "face": 2},
                    "tags": ["boundary_stated"],
                },
                "unlockAchievement": "chose_self_once",
            },
        ],
    },
    {
        "id": "major_pressure",
        "chapter": 4,
        "title": "一次重要的失败",
        "scene": "你认真准备了很久的比赛、申请或考核，结果没有达到预期。朋友圈里，别人看起来都在前进。你坐在教学楼外的台阶上，忽然很难判断：是自己不够好，还是只是这一次运气与时机都不站在你这边？",
        "anchor": "【现实锚点】邮箱拒信、朋友圈战报、一个人走回宿舍的路。",
        "choices": [
            {
                "text": "立刻复盘，把自己安排得更紧，不能再输。",
                "effects": {
                    "resources": {"career": 8, "energy": -7, "stability": -5},
                    "wounds": {"rejection": 8, "worth": 7, "control": 5},
                    "needs": {"achievement": 7, "control": 4},
                    "styles": {"face": 2, "selfBlame": 3, "reflect": 2},
                    "tags": ["double_down"],
                },
            },
            {
                "text": "先躲开一阵，不太想面对这件事。",
                "effects": {
                    "resources": {"energy": 2, "stability": -3, "career": -4},
                    "wounds": {"worth": 4, "rejection": 4},
                    "needs": {"recovery": 4, "safety": 3},
                    "styles": {"avoid": 3, "impulse": 1},
                    "tags": ["withdrawn"],
                },
            },
            {
                "text": "找一个信任的人聊，试着把失败和自我价值分开。",
                "effects": {
                    "resources": {"relationship": 5, "stability": 7},
                    "wounds": {"worth": 2, "rejection": 2},
                    "needs": {"seen": 7, "belonging": 5, "recovery": 3},
                    "styles": {"seekHelp": 3, "flexible": 2, "face": 1},
                    "tags": ["failure_processed"],
                },
            },
        ],
    },
    {
        "id": "relationship_or_friendship",
        "chapter": 5,
        "title": "一段重要关系开始变冷",
        "scene": "无论是喜欢的人、伴侣，还是一位非常重要的朋友，对方最近的回应都开始变慢。你反复点开对话框，又关掉。理智告诉你，不是所有冷淡都意味着失去；可情绪并不总听理智的。",
        "anchor": "【现实锚点】‘对方正在输入…’又消失，已读未回，深夜翻聊天记录。",
        "choices": [
            {
                "text": "不断确认：是不是我哪里做错了？",
                "effects": {
                    "resources": {"stability": -7, "relationship": -2},
                    "wounds": {"abandonment": 9, "worth": 5},
                    "needs": {"belonging": 7, "seen": 5},
                    "styles": {"please": 2, "selfBlame": 2, "face": 1},
                    "tags": ["fear_of_loss"],
                },
            },
            {
                "text": "先稳住自己，等情绪下来再沟通。",
                "effects": {
                    "resources": {"stability": 6, "relationship": 1},
                    "wounds": {"abandonment": 2},
                    "needs": {"safety": 4, "autonomy": 5},
                    "styles": {"reflect": 2, "flexible": 2, "face": 1},
                    "tags": ["self_soothed"],
                },
            },
            {
                "text": "不追了，直接把需要藏起来，当作无所谓。",
                "effects": {
                    "resources": {"stability": -2, "relationship": -4},
                    "wounds": {"neglect": 7, "abandonment": 5},
                    "needs": {"autonomy": 3, "seen": 6},
                    "styles": {"avoid": 2, "solo": 2},
                    "tags": ["shut_down"],
                },
            },
        ],
    },
    {
        "id": "internship",
        "chapter": 6,
        "title": "第一份实习与疲惫",
        "scene": "你拿到一份看起来不错的实习。节奏很快，要求很高，做得好时并不会被特别夸奖，出错时却会被立刻指出。你越来越像一个随时待命的人。某个周末，你盯着电脑，却怎么也提不起劲。",
        "anchor": "【现实锚点】工作群红点、未完成事项列表、地铁回程时的困意。",
        "choices": [
            {
                "text": "继续扛，先把这段履历做漂亮再说。",
                "effects": {
                    "resources": {"career": 9, "money": 4, "energy": -10, "stability": -7},
                    "wounds": {"overload": 8, "worth": 5},
                    "needs": {"achievement": 8, "safety": 3},
                    "styles": {"solo": 3, "selfBlame": 1, "face": 1},
                    "tags": ["keep_carrying", "burnout_risk"],
                },
            },
            {
                "text": "开始给自己留边界：按时下线，必要时说不。",
                "effects": {
                    "resources": {"energy": 7, "stability": 6, "career": -1},
                    "wounds": {"overload": 2, "control": 2},
                    "needs": {"autonomy": 7, "recovery": 6},
                    "styles": {"self": 3, "face": 2},
                    "tags": ["boundary_at_work"],
                },
                "unlockAchievement": "chose_self_once",
            },
            {
                "text": "先找前辈或朋友聊聊，看是不是只有我这样。",
                "effects": {
                    "resources": {"relationship": 4, "stability": 5, "energy": 2},
                    "wounds": {"worth": 2, "overload": 3},
                    "needs": {"seen": 6, "belonging": 4, "recovery": 3},
                    "styles": {"seekHelp": 3, "reflect": 1},
                    "tags": ["shared_pressure"],
                },
            },
        ],
    },
    {
        "id": "graduation",
        "chapter": 7,
        "title": "毕业去向",
        "scene": "你面前放着两封 offer 和一个尚未截止的报名入口。一个更稳定，一个更接近自己想做的事，另一个则是继续深造的可能。你知道无论怎么选，都很难同时留下安全、自由、关系和成就。",
        "anchor": "【现实锚点】offer 邮件、报名截止前 30 分钟、父母电话、租房平台收藏夹。",
        "choices": [
            {
                "text": "选最稳定、最可预期的路径。",
                "effects": {
                    "resources": {"money": 5, "stability": 7, "career": 4},
                    "wounds": {"control": 3, "neglect": 2},
                    "needs": {"safety": 9, "achievement": 3},
                    "styles": {"reflect": 2, "please": 1},
                    "tags": ["safe_future"],
                },
                "unlockAchievement": "hold_everything",
            },
            {
                "text": "选更想去的方向，即便未来更不确定。",
                "effects": {
                    "resources": {"career": 6, "stability": -3, "relationship": -1},
                    "wounds": {"rejection": 3, "control": 3},
                    "needs": {"autonomy": 9, "achievement": 4},
                    "styles": {"self": 3, "face": 2},
                    "tags": ["uncertain_but_true"],
                },
                "unlockAchievement": "freedom_over_safety",
            },
            {
                "text": "选让关系和陪伴成本最低的方案。",
                "effects": {
                    "resources": {"relationship": 6, "stability": 4, "career": 1},
                    "wounds": {"abandonment": 3, "overload": 2},
                    "needs": {"belonging": 8, "safety": 3},
                    "styles": {"please": 2, "reflect": 2},
                    "tags": ["stay_for_connection"],
                },
            },
        ],
    },
    {
        "id": "burnout_or_repair",
        "chapter": 8,
        "title": "你终于开始意识到自己也需要被照顾",
        "scene": "几年过去，外部轨迹逐渐成形，但你开始更清楚地意识到：有些累不是睡一觉就能缓过来，有些空也不是下一个目标能自动填满。你站在一个并不显眼、却很关键的转折点：继续按旧方式活，还是试着换一种方式对待自己？",
        "anchor": "【现实锚点】深夜回家后的安静房间、长期置顶的待办清单、一直没回的消息草稿。",
        "choices": [
            {
                "text": "继续往前冲，等以后稳定了再修复自己。",
                "effects": {
                    "resources": {"career": 5, "energy": -7, "stability": -8},
                    "wounds": {"overload": 5, "neglect": 6, "worth": 3},
                    "needs": {"achievement": 4, "safety": 2},
                    "styles": {"solo": 2, "selfBlame": 2, "avoid": 1},
                    "tags": ["delay_repair"],
                },
            },
            {
                "text": "停下来整理：哪些不是能力问题，而是旧模式在反复启动？",
                "effects": {
                    "resources": {"stability": 8, "energy": 5},
                    "wounds": {"rejection": -2, "abandonment": -2, "control": -2, "overload": -2, "neglect": -2, "worth": -2},
                    "needs": {"recovery": 9, "seen": 4, "autonomy": 4},
                    "styles": {"reflect": 3, "face": 2, "flexible": 2},
                    "tags": ["repair_begins"],
                },
            },
            {
                "text": "认真对一位重要的人说：‘我最近其实很累，也有点撑不住。’",
                "effects": {
                    "resources": {"relationship": 7, "stability": 6, "energy": 3},
                    "wounds": {"neglect": -2, "abandonment": -2},
                    "needs": {"seen": 8, "belonging": 7, "recovery": 4},
                    "styles": {"seekHelp": 3, "face": 1, "flexible": 1},
                    "tags": ["vulnerability_shared"],
                },
            },
        ],
    },
    {
        "id": "first_year_work",
        "chapter": 9,
        "title": "第一年工作里的隐形考核",
        "scene": "真正进入职场后，你发现很多考核并不写在制度里：谁回复得更快，谁更能接住临时需求，谁在会议里敢不敢表达不同意见。你做得不差，却总觉得自己还在被暗中观察。某天下班前，领导临时发来一项明早要用的材料。你已经连续几天睡得很少，窗外天色压下来，办公室的白光却还亮得刺眼。",
        "anchor": "【现实锚点】18:53 的工作消息、屏幕右下角的低电量提示、便利店加热饭的塑料盖。",
        "choices": [
            {
                "text": "接下来，今晚做完，至少别让人失望。",
                "effects": {
                    "resources": {"career": 7, "money": 2, "energy": -9, "stability": -5},
                    "wounds": {"overload": 7, "worth": 4, "neglect": 3},
                    "needs": {"achievement": 7, "safety": 4},
                    "styles": {"solo": 3, "please": 2, "selfBlame": 1},
                    "tags": ["after_hours_compliance", "invisible_exam"],
                },
            },
            {
                "text": "先确认优先级和交付范围，把能做和不能做说清楚。",
                "effects": {
                    "resources": {"career": 3, "energy": 3, "stability": 6},
                    "wounds": {"control": 2, "overload": -2},
                    "needs": {"control": 5, "autonomy": 6, "recovery": 2},
                    "styles": {"face": 2, "self": 2, "reflect": 2},
                    "tags": ["scope_clarified", "work_boundary"],
                },
                "unlockAchievement": "chose_self_once",
            },
            {
                "text": "请同事帮你对一下思路，别再一个人憋到凌晨。",
                "effects": {
                    "resources": {"relationship": 4, "energy": 2, "stability": 4, "career": 2},
                    "wounds": {"overload": -1, "worth": 1},
                    "needs": {"seen": 5, "belonging": 4, "control": 3},
                    "styles": {"seekHelp": 3, "face": 1, "flexible": 1},
                    "tags": ["work_support"],
                },
            },
            {
                "text": "你意识到这不是第一次，于是把“自动补位”写进复盘里。",
                "requiresAnyTags": ["keep_carrying", "delay_repair", "after_hours_compliance", "child_useful_role"],
                "effects": {
                    "resources": {"stability": 7, "energy": 2},
                    "wounds": {"overload": -3, "worth": -1},
                    "needs": {"recovery": 5, "seen": 3, "autonomy": 3},
                    "styles": {"reflect": 3, "flexible": 2, "face": 1},
                    "tags": ["pattern_named"],
                },
                "unlockAchievement": "pattern_seen",
            },
        ],
    },
    {
        "id": "family_expectation",
        "chapter": 10,
        "title": "家人开始谈论“稳定下来”",
        "scene": "你回家吃饭，桌上的话题很快绕到工作、收入、伴侣、买房、未来规划。家人并非全是恶意，他们只是把自己的焦虑包进“为你好”里。汤碗的热气慢慢散开，你听着听着，忽然分不清：哪些期待真的属于你，哪些只是你不敢辜负。",
        "anchor": "【现实锚点】饭桌上的沉默、亲戚群里的比较、回程路上车窗倒映出的脸。",
        "choices": [
            {
                "text": "顺着他们说，先让这顿饭平稳过去。",
                "effects": {
                    "resources": {"relationship": 4, "stability": -3},
                    "wounds": {"neglect": 5, "overload": 3},
                    "needs": {"belonging": 5, "safety": 4, "seen": 3},
                    "styles": {"please": 3, "avoid": 1},
                    "tags": ["family_peace_kept"],
                },
            },
            {
                "text": "把自己的节奏说出来：我会负责，但不想被催着证明。",
                "effects": {
                    "resources": {"stability": 6, "relationship": -1},
                    "wounds": {"rejection": 2, "control": 1},
                    "needs": {"autonomy": 7, "seen": 4, "control": 3},
                    "styles": {"self": 3, "face": 2},
                    "tags": ["family_boundary"],
                },
                "unlockAchievement": "chose_self_once",
            },
            {
                "text": "只说一半真实想法，给彼此都留一点缓冲。",
                "effects": {
                    "resources": {"relationship": 2, "stability": 2},
                    "wounds": {"control": 2},
                    "needs": {"safety": 4, "autonomy": 3},
                    "styles": {"reflect": 3, "flexible": 1},
                    "tags": ["soft_disclosure"],
                },
            },
            {
                "text": "你第一次承认：我怕的不是他们反对，而是我没有自己的答案。",
                "requiresAnyTags": ["compromise_path", "safe_path", "family_approved", "family_peace_kept", "rank_internalized"],
                "effects": {
                    "resources": {"stability": 5, "energy": 2},
                    "wounds": {"control": -2, "worth": -1},
                    "needs": {"seen": 5, "autonomy": 5, "recovery": 2},
                    "styles": {"reflect": 3, "flexible": 2},
                    "tags": ["borrowed_answer_seen"],
                },
                "unlockAchievement": "pattern_seen",
            },
        ],
    },
    {
        "id": "intimacy_conflict",
        "chapter": 11,
        "title": "一次真正需要说开的关系冲突",
        "scene": "重要关系里积攒的小事终于变成一次争执。对方说你总是不说清楚，却又希望别人能懂；你也委屈，因为很多时候你不是不想说，而是不确定说出来会不会被嫌麻烦。空气安静下来后，你们都在等对方先开口，手机屏幕暗了又亮，像一口没能喘匀的气。",
        "anchor": "【现实锚点】停在输入框里的长句、没洗的杯子、窗外已经暗下来的天。",
        "choices": [
            {
                "text": "先道歉，把事情压下去，别让关系继续变糟。",
                "effects": {
                    "resources": {"relationship": 3, "stability": -4},
                    "wounds": {"neglect": 5, "abandonment": 4},
                    "needs": {"belonging": 6, "safety": 3, "seen": 4},
                    "styles": {"please": 3, "avoid": 1, "selfBlame": 1},
                    "tags": ["conflict_smoothed"],
                },
            },
            {
                "text": "把真实需求说清楚：我不是要你负责我的情绪，但我需要回应。",
                "effects": {
                    "resources": {"relationship": 6, "stability": 5},
                    "wounds": {"abandonment": -2, "neglect": -2},
                    "needs": {"seen": 8, "belonging": 6, "autonomy": 3},
                    "styles": {"face": 3, "self": 2, "flexible": 1},
                    "tags": ["need_spoken_clearly"],
                },
                "unlockAchievement": "asked_clearly",
            },
            {
                "text": "先暂停争执，约定明天再谈，给情绪留出口。",
                "effects": {
                    "resources": {"stability": 5, "relationship": 1, "energy": 2},
                    "wounds": {"control": -1, "abandonment": 1},
                    "needs": {"recovery": 4, "safety": 4, "control": 3},
                    "styles": {"reflect": 2, "flexible": 2, "face": 1},
                    "tags": ["conflict_paused"],
                },
            },
            {
                "text": "如果这段关系一直只能靠你吞下去，你决定重新评估它。",
                "requiresAnyTags": ["shut_down", "conflict_smoothed", "family_peace_kept", "early_surface_peace"],
                "effects": {
                    "resources": {"relationship": -3, "stability": 6},
                    "wounds": {"neglect": -3, "abandonment": 2},
                    "needs": {"autonomy": 8, "seen": 4},
                    "styles": {"self": 3, "face": 2, "reflect": 1},
                    "tags": ["relationship_re_evaluated"],
                },
                "unlockAchievement": "chose_self_once",
            },
        ],
    },
    {
        "id": "return_to_self",
        "chapter": 12,
        "title": "回望：你想把人生还给谁",
        "scene": "某个普通的晚上，你整理旧物，翻到高考前的草稿纸、大学时的聊天截图、第一份实习的工牌、几张没发出去的备忘录。还有更早的东西：小学听写本的一角、初中排名表的复印件、某张集体照里站在边缘的自己。你忽然发现，人生并不是某一个选择决定的，而是很多次你如何对待自己的选择叠起来的。现在，你要给这一路一个暂时的答案。",
        "anchor": "【现实锚点】旧纸箱、备忘录搜索记录、窗台上的灰尘、很久没有认真问过自己的那句：我现在想怎么活？",
        "choices": [
            {
                "text": "继续把标准握紧一点。只要足够好，就会安全。",
                "effects": {
                    "resources": {"career": 6, "money": 3, "energy": -6, "stability": -5},
                    "wounds": {"worth": 5, "control": 4, "overload": 3},
                    "needs": {"achievement": 8, "safety": 5},
                    "styles": {"selfBlame": 2, "solo": 2, "face": 1},
                    "tags": ["standard_gripped"],
                },
            },
            {
                "text": "把一些期待放回原处：那是别人的焦虑，不全是我的任务。",
                "effects": {
                    "resources": {"stability": 8, "energy": 4},
                    "wounds": {"overload": -3, "neglect": -2, "worth": -2},
                    "needs": {"autonomy": 7, "recovery": 5, "seen": 3},
                    "styles": {"reflect": 3, "self": 2, "flexible": 2},
                    "tags": ["expectations_returned", "self_returned"],
                },
                "unlockAchievement": "return_to_self",
            },
            {
                "text": "给重要的人发消息：以后我想更早说出真实状态。",
                "effects": {
                    "resources": {"relationship": 7, "stability": 5, "energy": 2},
                    "wounds": {"abandonment": -2, "neglect": -2},
                    "needs": {"belonging": 7, "seen": 7, "recovery": 3},
                    "styles": {"seekHelp": 2, "face": 2, "flexible": 1},
                    "tags": ["connection_chosen", "self_returned"],
                },
                "unlockAchievement": "return_to_self",
            },
            {
                "text": "你决定正式开始修复：咨询、休息、记录，至少选一个真的做。",
                "requiresAnyTags": ["repair_begins", "pattern_named", "borrowed_answer_seen", "vulnerability_shared"],
                "effects": {
                    "resources": {"energy": 7, "stability": 9, "relationship": 2},
                    "wounds": {"rejection": -2, "abandonment": -2, "control": -2, "overload": -3, "neglect": -3, "worth": -3},
                    "needs": {"recovery": 9, "seen": 5, "autonomy": 5},
                    "styles": {"face": 2, "seekHelp": 2, "reflect": 2, "flexible": 2},
                    "tags": ["active_repair", "self_returned"],
                },
                "unlockAchievement": "repair_begins",
            },
        ],
    },
]

for _index, _node in enumerate(STORY_NODES, start=1):
    _node["chapter"] = _index


def clamp(n: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, n))


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path: Path, default):
    if not path.exists():
        return copy.deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return copy.deepcopy(default)


def save_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_initial_state():
    return {
        "startedAt": now_str(),
        "nodeIndex": 0,
        "finished": False,
        "resources": {
            "career": 50,
            "money": 50,
            "energy": 60,
            "relationship": 50,
            "stability": 55,
        },
        "wounds": {
            "rejection": 20,
            "abandonment": 20,
            "control": 20,
            "overload": 20,
            "neglect": 20,
            "worth": 20,
        },
        "needs": {
            "safety": 0,
            "seen": 0,
            "control": 0,
            "belonging": 0,
            "autonomy": 0,
            "achievement": 0,
            "recovery": 0,
        },
        "styles": {
            "face": 0,
            "avoid": 0,
            "self": 0,
            "please": 0,
            "seekHelp": 0,
            "solo": 0,
            "reflect": 0,
            "impulse": 0,
            "flexible": 0,
            "selfBlame": 0,
        },
        "tags": [],
        "choices": [],
        "unlockedAchievements": [],
        "chapterSummaries": [],
    }


def build_chapter_mirror(state, chapter):
    dominant_need = max(state["needs"], key=state["needs"].get)
    dominant_wound = max(state["wounds"], key=state["wounds"].get)
    lines = []

    if dominant_wound == "control":
        lines.append("这一章里，你对“不要失控”的在意很明显。你做的很多选择，并不只是为了得到结果，更像是在提前阻止最坏情况发生。")
    if dominant_wound == "abandonment":
        lines.append("这一章里，关系中的不确定感对你的影响很大。你并不只是怕失去一个人，而是怕再次经历那种“对方退开了，而你还不知道发生了什么”的感觉。")
    if dominant_wound == "worth":
        lines.append("这一章里，你很容易把结果和自我价值绑在一起。失败本来只是一次事件，但你更容易把它听成对自己的判词。")
    if dominant_wound == "overload":
        lines.append("这一章里，你很像那个总会自动补位的人。问题在于，长期扛责会让你逐渐分不清：哪些本来就不该全由你承担。")
    if dominant_need == "recovery":
        lines.append("你这一章真正缺的，可能不是再努力一点，而是恢复一点。很多看似拖延、迟缓或无力，其实更像长期透支后的后坐力。")
    if dominant_need == "seen":
        lines.append("你这一章真正想要的，不一定是建议，而是被认真看见。被看见和被评价不是一回事。")
    if dominant_need == "autonomy":
        lines.append("你这一章明显在争取“由我来决定”。这种需求未必总是激烈地表达出来，但它一直在底层推动你的选择。")

    if not lines:
        lines.append("这一章里，你没有完全被某一种模式牵着走。你在犹豫、权衡和试探中前进，这本身也说明你正在寻找更适合自己的活法。")

    return {
        "chapter": chapter,
        "title": f"第 {chapter} 章镜像",
        "content": " ".join(lines[:2]),
    }


def choice_is_available(choice, state):
    tags = set(state.get("tags", []))
    required_any = set(choice.get("requiresAnyTags", []))
    required_all = set(choice.get("requiresAllTags", []))
    excluded = set(choice.get("excludesAnyTags", []))

    if required_any and not (required_any & tags):
        return False
    if required_all and not required_all.issubset(tags):
        return False
    if excluded and (excluded & tags):
        return False
    return True


def get_current_node(state):
    if state.get("finished"):
        return None
    return STORY_NODES[state["nodeIndex"]]


def get_available_choices(node, state):
    return [(idx, choice) for idx, choice in enumerate(node["choices"]) if choice_is_available(choice, state)]


def choose(state, choice_index):
    node = get_current_node(state)
    if node is None:
        raise ValueError("当前人生已经结束，不能继续选择。")
    available = dict(get_available_choices(node, state))
    if choice_index not in available:
        raise ValueError(f"当前节点不可选择选项：{choice_index}")
    return apply_choice(state, node, available[choice_index], choice_index)


def simulate_life(choice_indexes=None, default_choice=0):
    state = create_initial_state()
    choice_indexes = choice_indexes or []
    while not state["finished"]:
        node = get_current_node(state)
        available = get_available_choices(node, state)
        wanted = choice_indexes[state["nodeIndex"]] if state["nodeIndex"] < len(choice_indexes) else default_choice
        available_indexes = [idx for idx, _ in available]
        selected = wanted if wanted in available_indexes else available_indexes[0]
        state = choose(state, selected)
    return state, build_final_report(state)


def render_story_map(state):
    st.subheader("剧情树路径")
    choice_by_chapter = {item["chapter"]: item for item in state["choices"]}
    current_node = get_current_node(state)
    current_chapter = current_node["chapter"] if current_node else None
    for node in STORY_NODES:
        selected = choice_by_chapter.get(node["chapter"])
        if selected:
            st.write(f"✓ 第 {node['chapter']} 章：{node['title']}")
        elif node["chapter"] == current_chapter:
            st.write(f"▶ 第 {node['chapter']} 章：{node['title']}")
        else:
            st.write(f"○ 第 {node['chapter']} 章：{node['title']}")


def apply_choice(state, node, choice, choice_index):
    next_state = copy.deepcopy(state)
    effects = choice.get("effects", {})

    for k, v in effects.get("resources", {}).items():
        next_state["resources"][k] = clamp(next_state["resources"].get(k, 0) + v)

    for k, v in effects.get("wounds", {}).items():
        next_state["wounds"][k] = clamp(next_state["wounds"].get(k, 0) + v)

    for k, v in effects.get("needs", {}).items():
        next_state["needs"][k] = clamp(next_state["needs"].get(k, 0) + v, 0, 999)

    for k, v in effects.get("styles", {}).items():
        next_state["styles"][k] = next_state["styles"].get(k, 0) + v

    next_state["tags"].extend(effects.get("tags", []))
    next_state["choices"].append({
        "nodeId": node["id"],
        "nodeTitle": node["title"],
        "choiceIndex": choice_index,
        "choiceText": choice["text"],
        "chapter": node["chapter"],
        "at": now_str(),
    })

    unlock = choice.get("unlockAchievement")
    if unlock and unlock not in next_state["unlockedAchievements"]:
        next_state["unlockedAchievements"].append(unlock)

    if node["chapter"] == 1 and "first_step" not in next_state["unlockedAchievements"]:
        next_state["unlockedAchievements"].append("first_step")

    chapter_summary = build_chapter_mirror(next_state, node["chapter"])
    next_state["chapterSummaries"] = [x for x in next_state["chapterSummaries"] if x["chapter"] != node["chapter"]]
    next_state["chapterSummaries"].append(chapter_summary)

    next_state["nodeIndex"] += 1
    if next_state["nodeIndex"] >= len(STORY_NODES):
        next_state["finished"] = True

    return next_state


def determine_ending(state):
    r = state["resources"]
    w = state["wounds"]
    s = state["styles"]
    n = state["needs"]

    if "active_repair" in state["tags"] or (
        "self_returned" in state["tags"] and s["flexible"] >= s["selfBlame"] and n["recovery"] >= 18
    ):
        return "quiet_repair"
    if "self_returned" in state["tags"] and n["autonomy"] >= 18 and r["stability"] >= 55:
        return "integrated_self"
    if r["career"] >= 72 and r["stability"] <= 40 and w["neglect"] >= 30 and s["please"] >= s["self"]:
        return "hollow_success"
    if n["autonomy"] >= 16 and r["stability"] < 55 and "uncertain_but_true" in state["tags"]:
        return "free_but_unstable"
    if s["please"] >= 4 and n["belonging"] >= 10 and r["relationship"] >= 55 and r["stability"] <= 50:
        return "everyone_happy_except_you"
    if r["energy"] <= 38 and w["overload"] >= 28:
        return "exhausted_survivor"
    if r["relationship"] >= 65 and (n["seen"] + n["belonging"]) >= 20:
        return "connected_and_warm"
    return "delayed_bloom"


def compute_achievements(state, ending_id):
    unlocked = set(state.get("unlockedAchievements", []))
    safe_tags = sum(t in ["safe_path", "safe_future", "family_approved"] for t in state["tags"])
    freedom_tags = sum(t in ["autonomy_path", "uncertain_but_true", "boundary_at_work", "family_boundary", "self_returned"] for t in state["tags"])

    if state["styles"].get("seekHelp", 0) <= 1:
        unlocked.add("no_one_bothered")
    if safe_tags >= 2:
        unlocked.add("hold_everything")
    if freedom_tags >= 2:
        unlocked.add("freedom_over_safety")
    if state["resources"]["energy"] <= 30 and state["finished"]:
        unlocked.add("still_standing")
    if state["resources"]["relationship"] >= 62:
        unlocked.add("soft_connection")
    if ending_id == "hollow_success":
        unlocked.add("hidden_branch_hollow")
    if "pattern_named" in state["tags"] or "borrowed_answer_seen" in state["tags"]:
        unlocked.add("pattern_seen")
    if "need_spoken_clearly" in state["tags"]:
        unlocked.add("asked_clearly")
    if "repair_begins" in state["tags"] or "active_repair" in state["tags"] or ending_id == "quiet_repair":
        unlocked.add("repair_begins")
    if "self_returned" in state["tags"] or ending_id == "integrated_self":
        unlocked.add("return_to_self")

    return sorted(unlocked)


def build_final_report(state):
    ending_id = determine_ending(state)
    ending = ENDING_DICTIONARY[ending_id]
    achievements = compute_achievements(state, ending_id)

    sorted_needs = sorted(state["needs"].items(), key=lambda x: x[1], reverse=True)
    sorted_wounds = sorted(state["wounds"].items(), key=lambda x: x[1], reverse=True)

    top_needs = [LABELS["needs"][k] for k, _ in sorted_needs[:3]]
    top_wounds = [LABELS["wounds"][k] for k, _ in sorted_wounds[:2]]

    styles = state["styles"]
    style_summary = [
        "你多数时候更倾向于面对问题，而不是完全躲开。" if styles["face"] >= styles["avoid"] else "你更容易先回避不适，等情绪下降后再处理问题。",
        "在关键节点里，你更愿意争取自己的边界。" if styles["self"] >= styles["please"] else "在关键节点里，你更容易优先维持关系与气氛。",
        "你并非总是独自承担，必要时会尝试向外连接。" if styles["seekHelp"] >= styles["solo"] else "你很习惯自己消化压力，这让你显得可靠，也更容易被忽略。",
        "你在部分节点里已经开始把失败与自我价值分开。" if styles["flexible"] >= styles["selfBlame"] else "你仍然容易把不顺利听成对自己的否定。",
    ]

    interpretations = []
    if "失控恐惧" in top_wounds:
        interpretations.append("你反复在意的，往往不是单一结果，而是局面脱离掌控后的连锁后果。你做很多准备，不只是为了成功，也是在避免慌乱。")
    if "遗弃敏感" in top_wounds:
        interpretations.append("关系中的模糊、冷淡和未被回应，对你的影响比你表面表现出来的更大。你可能不是单纯缺陪伴，而是很怕自己再次站在不被选择的位置。")
    if "价值感脆弱" in top_wounds:
        interpretations.append("你在多个节点里把结果与自我价值绑得比较紧。很多时候，真正让你难受的不是失利本身，而是“是不是我不够好”这个问题被再次触发。")
    if "责任过载" in top_wounds:
        interpretations.append("你习惯补位、扛责、维持运转，这种能力会让你在团队和关系里显得很可靠，但也容易让别人默认你还能继续承担。")
    if "休息与修复" in top_needs:
        interpretations.append("你当前最缺的也许不是新的目标，而是恢复。继续硬扛会让很多问题看起来像能力问题，但它们未必真的是。")
    if "被看见" in top_needs:
        interpretations.append("你当前明显需要被理解，而不是再被指导一次。你真正想听见的，也许不是“你应该怎么做”，而是“我知道这对你来说为什么难”。")
    if "自主与边界" in top_needs:
        interpretations.append("你现在很需要替自己做主。这个需求不一定表现为激烈对抗，也可能只是想终于允许自己承认：我其实并不想再那样活了。")

    if not interpretations:
        interpretations.append("你的这局人生并没有被一种模式完全垄断。你在矛盾中尝试了不同路径，这说明你仍有空间重写自己的解释方式。")

    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "createdAt": now_str(),
        "endingId": ending_id,
        "endingTitle": ending["title"],
        "endingSummary": ending["summary"],
        "topNeeds": top_needs,
        "topWounds": top_wounds,
        "stylesSummary": style_summary,
        "interpretation": " ".join(interpretations),
        "mostRecentChoice": state["choices"][-1]["choiceText"] if state["choices"] else "无",
        "achievements": achievements,
        "snapshot": copy.deepcopy(state),
    }


def persist_current_state(state):
    save_json(CURRENT_SAVE_FILE, state)


def load_current_state():
    return load_json(CURRENT_SAVE_FILE, None)


def clear_current_state():
    if CURRENT_SAVE_FILE.exists():
        CURRENT_SAVE_FILE.unlink()


def load_archive():
    return load_json(ARCHIVE_FILE, [])


def save_archive(archive):
    save_json(ARCHIVE_FILE, archive)


def load_achievements():
    return load_json(ACHIEVEMENTS_FILE, [])


def save_achievements(achievements):
    save_json(ACHIEVEMENTS_FILE, achievements)


def render_progress_bars(state):
    st.subheader("当前资源")
    for k, v in state["resources"].items():
        st.write(f"**{LABELS['resources'][k]}：{v}**")
        st.progress(int(v))

    st.subheader("当前需求趋势")
    sorted_needs = sorted(state["needs"].items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_needs:
        display_v = min(int(v * 5), 100)
        st.write(f"**{LABELS['needs'][k]}：{v}**")
        st.progress(display_v)


def render_home():
    st.title("命运回响 · 文本版原型")
    st.caption("现实人生模拟 · 需求拆解 · 多周目存档")

    st.markdown(
        """
你将经历一条现实人生线，从小学、初中到高考、大学，再到初入社会后的回望。  
系统不会告诉你“该怎么活”，也不会给你贴上武断标签。  
它只会记录你在关键节点中的反复选择，帮助你看见：你一直在保护什么，又真正渴望什么。
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("新的人生", use_container_width=True):
            state = create_initial_state()
            st.session_state["game_state"] = state
            persist_current_state(state)
            st.session_state["page"] = "game"
            st.rerun()

    with col2:
        current = load_current_state()
        disabled = current is None or current.get("finished", False)
        if st.button("继续存档", use_container_width=True, disabled=disabled):
            st.session_state["game_state"] = current
            st.session_state["page"] = "game"
            st.rerun()

    with col3:
        if st.button("查看档案馆", use_container_width=True):
            st.session_state["page"] = "archive"
            st.rerun()

    with col4:
        if st.button("产品说明", use_container_width=True):
            st.session_state["page"] = "guide"
            st.rerun()

    st.divider()
    archive = load_archive()
    achievements = load_achievements()

    c1, c2 = st.columns(2)
    c1.metric("历史存档", len(archive))
    c2.metric("已解锁成就", len(achievements))

    with st.expander("产品边界说明"):
        st.markdown(
            """
- 本原型是互动式自我觉察工具，不提供医学诊断、心理疾病判断或替代心理咨询。  
- “受伤线索”“当前需求”“决策风格”均为基于剧情路径的规则化解释，用于帮助用户拆解问题，而非给出专业结论。  
- 如遇强烈不适或危机状态，应寻求现实中的专业支持系统。
            """
        )


def render_guide():
    st.title("产品使用说明")
    st.caption("给体验者、组织者和二次开发者看的完整说明")

    for title, content in PRODUCT_GUIDE.items():
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.markdown(content.strip())

    st.divider()
    st.markdown("### 推荐交付方式")
    st.write("把整个文件夹交给别人。对方双击 `一键启动.bat`，脚本会自动创建本地虚拟环境、安装依赖并打开浏览器。")
    st.write("如果对方电脑没有 Python，请先运行 `安装说明.md` 中的 Python 安装步骤，之后不需要再手动配置命令行环境。")

    if st.button("返回首页", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()


def render_game():
    state = st.session_state["game_state"]
    node = STORY_NODES[state["nodeIndex"]]

    st.title(f"第 {node['chapter']} 章 · {node['title']}")
    st.caption(f"当前存档开始时间：{state['startedAt']}")

    left, right = st.columns([2, 1])

    with left:
        st.markdown(f"### 场景")
        st.write(node["scene"])
        st.info(node["anchor"])

        chapter = node["chapter"]
        previous_summary = None
        for item in state["chapterSummaries"]:
            if item["chapter"] == chapter - 1:
                previous_summary = item
                break
        if previous_summary:
            st.success(f"**{previous_summary['title']}**\n\n{previous_summary['content']}")

        st.markdown("### 你会怎么选？")
        available_choices = get_available_choices(node, state)
        for idx, choice in available_choices:
            if st.button(choice["text"], key=f"choice_{node['id']}_{idx}", use_container_width=True):
                next_state = apply_choice(state, node, choice, idx)
                st.session_state["game_state"] = next_state
                persist_current_state(next_state)
                if next_state["finished"]:
                    report = build_final_report(next_state)
                    archive = load_archive()
                    archive.insert(0, report)
                    save_archive(archive)

                    all_achievements = sorted(set(load_achievements()) | set(report["achievements"]))
                    save_achievements(all_achievements)

                    clear_current_state()
                    st.session_state["report"] = report
                    st.session_state["page"] = "report"
                st.rerun()

        st.divider()
        st.markdown("### 已走过的节点")
        if not state["choices"]:
            st.write("你的人生还刚开始。")
        else:
            for item in state["choices"]:
                with st.container(border=True):
                    st.write(f"**{item['nodeTitle']}**")
                    st.write(item["choiceText"])

    with right:
        render_progress_bars(state)
        render_story_map(state)
        st.subheader("当前阶段")
        st.write(f"已完成节点：{len(state['choices'])}")
        st.write(f"隐藏标签数：{len(state['tags'])}")

        if st.button("返回首页", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()


def render_report():
    report = st.session_state["report"]
    state = report["snapshot"]

    st.title(report["endingTitle"])
    st.caption(f"终局报告 · {report['createdAt']}")

    st.markdown("### 这一局人生的总结")
    st.write(report["endingSummary"])
    st.write(report["interpretation"])

    st.markdown("### 你当前更显著的需求")
    st.write("、".join(report["topNeeds"]))

    st.markdown("### 更容易反复启动的受伤线索")
    st.write("、".join(report["topWounds"]))

    st.markdown("### 决策风格摘要")
    for line in report["stylesSummary"]:
        st.write(f"- {line}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 资源终值")
        for k, v in state["resources"].items():
            st.write(f"**{LABELS['resources'][k]}：{v}**")
            st.progress(int(v))

    with col2:
        st.markdown("### 解锁成就")
        if report["achievements"]:
            for a in report["achievements"]:
                st.write(f"- {ACHIEVEMENTS_DICTIONARY.get(a, {}).get('title', a)}")
        else:
            st.write("本局未解锁成就。")

    st.markdown("### 最后一个关键节点")
    st.write(report["mostRecentChoice"])

    st.markdown("### 下一局可以尝试什么？")
    st.write("- 在你最想维持体面的位置，试着优先一次真实需求。")
    st.write("- 在你最容易独自承担的位置，试着向外说出一次“我需要帮助”。")
    st.write("- 在你最怕失控的位置，试着先允许自己不那么完美。")

    c1, c2, c3 = st.columns(3)
    if c1.button("再开一局", use_container_width=True):
        state = create_initial_state()
        st.session_state["game_state"] = state
        persist_current_state(state)
        st.session_state["page"] = "game"
        st.rerun()

    if c2.button("查看档案馆", use_container_width=True):
        st.session_state["page"] = "archive"
        st.rerun()

    if c3.button("返回首页", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()


def render_archive():
    archive = load_archive()
    achievements = load_achievements()

    st.title("档案馆")
    st.caption("你已经活过的几种人生")

    tab1, tab2, tab3 = st.tabs(["存档列表", "成就总览", "平行人生对照"])

    with tab1:
        if not archive:
            st.write("还没有历史存档。")
        else:
            for item in archive:
                with st.container(border=True):
                    st.write(f"### {item['endingTitle']}")
                    st.caption(item["createdAt"])
                    st.write(item["endingSummary"])
                    st.write(f"需求：{'、'.join(item['topNeeds'])}")
                    st.write(f"线索：{'、'.join(item['topWounds'])}")

    with tab2:
        for item in ACHIEVEMENTS_DICTIONARY.values():
            unlocked = item["id"] in achievements
            with st.container(border=True):
                st.write(f"**{item['title']}**")
                st.write(item["desc"])
                st.write(f"状态：{'已解锁' if unlocked else '未解锁'}")

    with tab3:
        if len(archive) < 2:
            st.write("至少需要两个存档才能进行对照。")
        else:
            labels = [f"{x['endingTitle']} · {x['createdAt']}" for x in archive]
            left_label = st.selectbox("左侧人生", labels, index=0)
            right_label = st.selectbox("右侧人生", labels, index=1)

            left = archive[labels.index(left_label)]
            right = archive[labels.index(right_label)]

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"### {left['endingTitle']}")
                st.write(f"需求：{'、'.join(left['topNeeds'])}")
                st.write(f"线索：{'、'.join(left['topWounds'])}")

            with c2:
                st.markdown(f"### {right['endingTitle']}")
                st.write(f"需求：{'、'.join(right['topNeeds'])}")
                st.write(f"线索：{'、'.join(right['topWounds'])}")

            common = sorted(set(left["topWounds"]) & set(right["topWounds"]))
            st.info(
                f"对照解释：左侧人生更明显地指向“{left['topNeeds'][0]}”，右侧人生更明显地指向“{right['topNeeds'][0]}”。"
                + (f" 两局共同的受伤线索是：{'、'.join(common)}。" if common else " 这两局没有共享最高层级的受伤线索。")
            )

    if st.button("返回首页", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()


def main():
    st.set_page_config(page_title="命运回响 · 文本版原型", page_icon="📘", layout="wide")
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("game_state", create_initial_state())
    st.session_state.setdefault("report", None)

    with st.sidebar:
        st.markdown("## 导航")
        if st.button("首页", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
        if st.button("档案馆", use_container_width=True):
            st.session_state["page"] = "archive"
            st.rerun()
        if st.button("产品说明", use_container_width=True):
            st.session_state["page"] = "guide"
            st.rerun()

        st.divider()
        st.markdown("### 技术说明")
        st.caption("本版本为 Streamlit 文本原型。")
        st.caption(f"数据会保存在：{SAVE_DIR}")

    page = st.session_state["page"]
    if page == "home":
        render_home()
    elif page == "game":
        render_game()
    elif page == "report":
        render_report()
    elif page == "archive":
        render_archive()
    elif page == "guide":
        render_guide()
    else:
        st.session_state["page"] = "home"
        st.rerun()


if __name__ == "__main__":
    main()
