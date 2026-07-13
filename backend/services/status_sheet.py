"""状态栏生成服务 - SillyTavern 格式"""
import json
from typing import Optional
from .llm import call_llm, call_llm_json


# 状态栏预设模板
PRESETS = {
    "default": {
        "name": "默认状态栏",
        "fields": [
            {"key": "name", "label": "姓名", "type": "text"},
            {"key": "mood", "label": "心情", "type": "text"},
            {"key": "location", "label": "位置", "type": "text"},
            {"key": "health", "label": "生命值", "type": "bar", "max": 100},
            {"key": "energy", "label": "体力", "type": "bar", "max": 100},
            {"key": "affection", "label": "好感度", "type": "bar", "max": 100},
        ],
    },
    "rpg": {
        "name": "RPG状态栏",
        "fields": [
            {"key": "name", "label": "姓名", "type": "text"},
            {"key": "class", "label": "职业", "type": "text"},
            {"key": "level", "label": "等级", "type": "number"},
            {"key": "hp", "label": "HP", "type": "bar", "max": 100},
            {"key": "mp", "label": "MP", "type": "bar", "max": 100},
            {"key": "attack", "label": "攻击", "type": "number"},
            {"key": "defense", "label": "防御", "type": "number"},
            {"key": "speed", "label": "速度", "type": "number"},
        ],
    },
    "visual_novel": {
        "name": "视觉小说状态栏",
        "fields": [
            {"key": "name", "label": "姓名", "type": "text"},
            {"key": "mood", "label": "心情", "type": "emoji"},
            {"key": "affection", "label": "好感度", "type": "bar", "max": 100},
            {"key": "trust", "label": "信任度", "type": "bar", "max": 100},
            {"key": "relationship", "label": "关系", "type": "text"},
        ],
    },
    "simple": {
        "name": "简约状态栏",
        "fields": [
            {"key": "mood", "label": "心情", "type": "emoji"},
            {"key": "energy", "label": "体力", "type": "bar", "max": 100},
            {"key": "affection", "label": "好感", "type": "bar", "max": 100},
        ],
    },
}


def render_bar(value: int, max_val: int = 100, width: int = 10) -> str:
    """渲染进度条"""
    ratio = min(max(value / max_val, 0), 1)
    filled = round(ratio * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {value}/{max_val}"


def render_status_html(data: dict, preset: str = "default") -> str:
    """渲染状态栏为HTML"""
    template = PRESETS.get(preset, PRESETS["default"])
    rows = []

    for field in template["fields"]:
        key = field["key"]
        label = field["label"]
        ftype = field["type"]
        value = data.get(key, "")

        if ftype == "bar":
            max_val = field.get("max", 100)
            val = int(value) if str(value).isdigit() else 0
            bar = render_bar(val, max_val)
            rows.append(f'<div class="status-row"><span class="label">{label}</span><span class="bar">{bar}</span></div>')
        elif ftype == "emoji":
            rows.append(f'<div class="status-row"><span class="label">{label}</span><span class="emoji">{value}</span></div>')
        elif ftype == "number":
            rows.append(f'<div class="status-row"><span class="label">{label}</span><span class="value">{value}</span></div>')
        else:
            rows.append(f'<div class="status-row"><span class="label">{label}</span><span class="text">{value}</span></div>')

    return f"""<div class="status-sheet">
  <div class="status-title">{template['name']}</div>
  {"".join(rows)}
</div>"""


def render_status_text(data: dict, preset: str = "default") -> str:
    """渲染状态栏为纯文本"""
    template = PRESETS.get(preset, PRESETS["default"])
    lines = [f"═══ {template['name']} ═══"]

    for field in template["fields"]:
        key = field["key"]
        label = field["label"]
        ftype = field["type"]
        value = data.get(key, "")

        if ftype == "bar":
            max_val = field.get("max", 100)
            val = int(value) if str(value).isdigit() else 0
            lines.append(f"  {label}: {render_bar(val, max_val)}")
        elif ftype == "emoji":
            lines.append(f"  {label}: {value}")
        else:
            lines.append(f"  {label}: {value}")

    lines.append("═" * 30)
    return "\n".join(lines)


async def generate_status_data(character_name: str, context: str = "") -> dict:
    """AI 生成角色状态数据"""
    system = """你是角色状态栏数据生成专家。根据角色信息生成初始状态数据。
输出JSON，数值在0-100之间：
{
  "name": "角色名",
  "mood": "当前心情emoji",
  "location": "当前位置",
  "health": 100,
  "energy": 80,
  "affection": 50,
  "trust": 30
}"""

    prompt = f"为角色「{character_name}」生成初始状态数据。\n上下文：{context[:1000] if context else '无'}"
    return await call_llm_json(prompt, system=system)


def get_presets() -> list:
    """获取所有状态栏预设"""
    return [
        {"id": k, "name": v["name"], "fields": v["fields"]}
        for k, v in PRESETS.items()
    ]
