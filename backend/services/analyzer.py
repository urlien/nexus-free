"""AI 角色分析管道
长文炼化管线（v1.0 重构）：
  1. 分块扫描 → 全局角色名单 + 别名
  2. 按角色聚合文本 → 定向提取完整档案
  3. 合并去重 → 输出结构化角色信息
"""
import json
import re
import asyncio
from typing import Optional

from .llm import call_llm, call_llm_json
from ..models.character import CharacterInfo, CharacterCard

# 分块参数
CHUNK_SIZE = 12000          # 每块字符数（约 6000-8000 汉字）
SCAN_CONCURRENCY = 3        # 扫描阶段并发数（Gemini 免费额度有限，别开太大）
EXTRACT_CONCURRENCY = 2     # 定向提取并发数
MAX_CHUNKS = 200            # 安全上限，防止误传超长文本把额度烧光


# ============ 工具函数 ============

def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """按段落切块，尽量不截断句子"""
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    paragraphs = text.split("\n")
    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 1 <= chunk_size:
            buf += p + "\n"
        else:
            if buf:
                chunks.append(buf.strip())
            # 单段太长，硬切
            if len(p) > chunk_size:
                for i in range(0, len(p), chunk_size):
                    chunks.append(p[i:i+chunk_size])
                buf = ""
            else:
                buf = p + "\n"
    if buf.strip():
        chunks.append(buf.strip())
    return chunks[:MAX_CHUNKS]


def _safe_json(result, default):
    """LLM 返回异常时的兜底"""
    if isinstance(result, dict) and "error" in result:
        return default
    if result is None:
        return default
    return result


# ============ 第一步：全局识人 ============

async def scan_characters_in_chunk(chunk: str, idx: int) -> list[dict]:
    """扫描单个文本块，找出所有被提及的角色"""
    system = """你是角色识别专家。从给定文本中找出所有出现的角色人物（不包括只被提到的地名、物品、组织）。

只输出 JSON 数组，每个元素：
{
  "name": "角色正式名",
  "aliases": ["文中出现的其他称呼"],
  "is_major": true/false,
  "evidence": "一句话说明他在文中有多重要"
}

判断 is_major：有台词、有独立描写、推动剧情的是 major；只被顺口提到的是 false。
找不到角色就输出 []。"""

    prompt = f"""文本块 #{idx + 1}：

---
{chunk}
---

请输出识别到的角色 JSON 数组。"""

    result = await call_llm_json(prompt, system=system, max_tokens=4096)
    arr = _safe_json(result, [])
    if isinstance(arr, dict):
        arr = arr.get("characters", []) or arr.get("result", [])
    if not isinstance(arr, list):
        return []
    # 简单清洗
    clean = []
    for item in arr:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        aliases = item.get("aliases") or []
        if not isinstance(aliases, list):
            aliases = [str(aliases)]
        clean.append({
            "name": name,
            "aliases": [str(a).strip() for a in aliases if str(a).strip()],
            "is_major": bool(item.get("is_major", False)),
            "evidence": str(item.get("evidence", "")),
        })
    return clean


async def build_character_roster(text: str) -> dict:
    """全文扫描，汇总去重后的角色名单
    返回: {name: {"aliases": set, "major": bool, "chunks": [索引]}}
    """
    chunks = split_text(text)
    sem = asyncio.Semaphore(SCAN_CONCURRENCY)

    async def _one(i, c):
        async with sem:
            try:
                return i, await scan_characters_in_chunk(c, i)
            except Exception as e:
                return i, []

    tasks = [_one(i, c) for i, c in enumerate(chunks)]
    results = await asyncio.gather(*tasks)

    roster: dict[str, dict] = {}
    for i, items in results:
        for item in items:
            name = item["name"]
            entry = roster.setdefault(name, {"aliases": set(), "major": False, "chunks": set()})
            entry["aliases"].update(item["aliases"])
            entry["major"] = entry["major"] or item["is_major"]
            entry["chunks"].add(i)

    # 把集合转成排序后的列表
    for k, v in roster.items():
        v["aliases"] = sorted(v["aliases"])
        v["chunks"] = sorted(v["chunks"])

    return {"chunks": chunks, "roster": roster}


# ============ 第二步：定向提取 ============

async def extract_character_deep(name: str, aliases: list[str], text: str, source: str = "") -> CharacterInfo:
    """针对某个角色，从与它相关的文本里提取完整档案"""
    names = [name] + [a for a in aliases if a]
    name_hint = "、".join(names)

    system = """你是资深角色设定师。请严格提取**目标角色**的信息，输出严格 JSON。

【最高限制】
1. 输出 JSON 里的 name 字段，必须严格等于给定目标角色名，绝不能因为文本里提到别人就改成别人。
2. 必须分清"谁在说话"和"在谈论谁"。文本里频繁出现的其他角色只是背景和关系，目标角色才是主角。
3. 缺失字段留空，不要编造。所有描述必须有文本依据。

输出结构：
{
  "name": "角色正式名",
  "aliases": ["别名"],
  "source_works": ["出处作品"],
  "description": "200字以上的角色概述，涵盖身份、背景、核心矛盾",
  "personality": "性格特征描述（具体，不要形容词堆砌）",
  "appearance": "外貌描述（有就写，没有留空）",
  "speech_pattern": "说话方式、口癖、语速、常用词",
  "relations": [{"name": "关系人", "relation": "关系类型", "detail": "具体描述"}],
  "likes": ["喜欢的事物"],
  "dislikes": ["讨厌的事物"],
  "habits": ["习惯、癖好"],
  "goal": "目标 / 动机 / 恐惧",
  "scenario": "一个适合作为角色扮演开场的情境（时间、地点、氛围、正在发生什么）",
  "first_message": "角色在这个情境下开口说的第一段话，符合其说话方式",
  "message_examples": ["符合角色说话风格的对话示例，3-5条"]
}"""

    prompt = f"""目标角色：{name_hint}
出处：{source or "未知"}

【最高指令】输出的 name 字段必须严格等于目标角色名，绝不能写成别的角色名。

以下是与该角色相关的原文（可能跨多个片段，已拼接）：

---
{text}
---

请提取该角色的完整信息。"""

    result = await call_llm_json(prompt, system=system, max_tokens=8192)
    result = _safe_json(result, {})

    return CharacterInfo(
        name=result.get("name", name),
        aliases=result.get("aliases", aliases) or aliases,
        source_works=result.get("source_works", [source] if source else []),
        description=result.get("description", ""),
        personality=result.get("personality", ""),
        appearance=result.get("appearance", ""),
        speech_pattern=result.get("speech_pattern", ""),
        relations=result.get("relations", []),
        likes=result.get("likes", []),
        dislikes=result.get("dislikes", []),
        habits=result.get("habits", []),
        goal=result.get("goal", ""),
        scenario=result.get("scenario", ""),
        first_message=result.get("first_message", ""),
        message_examples=result.get("message_examples", []),
    )


async def collect_character_context(chunks: list[str], chunk_ids: list[int], names: list[str], max_chars: int = 60000) -> str:
    """从指定块中，抽取与角色相关的段落，拼接成定向上下文"""
    pattern = "|".join(re.escape(n) for n in names if n)
    if not pattern:
        pattern = re.escape(names[0]) if names else ""

    picked = []
    total = 0
    for idx in chunk_ids:
        chunk = chunks[idx]
        paragraphs = chunk.split("\n")
        for p in paragraphs:
            if re.search(pattern, p):
                picked.append(p.strip())
                total += len(p)
                if total >= max_chars:
                    break
        if total >= max_chars:
            break

    # 如果一个相关段落都没抓到，就退回原文拼接
    if not picked:
        picked = [chunks[i] for i in chunk_ids]
    return "\n".join(picked)[:max_chars]


# ============ 主管线：长文炼化 ============

async def process_long_text(text: str, title: str = "") -> dict:
    """长文炼化主管线：
    1. 分块扫描 → 全局角色名单
    2. 只对 major 角色做定向提取
    3. 每个角色聚合相关段落 → 提取档案
    """
    if not text or len(text.strip()) < 50:
        return {"title": title, "error": "文本太短，至少 50 字"}

    # Step 1: 全局识人
    roster_data = await build_character_roster(text)
    chunks = roster_data["chunks"]
    roster = roster_data["roster"]

    major_chars = [(n, v) for n, v in roster.items() if v["major"]]
    minor_count = len(roster) - len(major_chars)

    if not major_chars:
        # 没有 major，退一步取所有识别的角色
        major_chars = list(roster.items())

    # Step 2: 定向提取
    sem = asyncio.Semaphore(EXTRACT_CONCURRENCY)

    async def _extract_one(name, meta):
        async with sem:
            names = [name] + meta["aliases"]
            ctx = await collect_character_context(chunks, meta["chunks"], names)
            try:
                info = await extract_character_deep(name, meta["aliases"], ctx, title)
                info.name = name  # 强制锁死名字，绝不让模型乱改
                # 过滤掉非人名的关系（如"心声·二"、"凝音·二"）
                bad_keys = ["心声", "凝音", "普攻", "重击", "共鸣", "变奏", "延奏", "闲趣", "突破"]
                info.relations = [r for r in info.relations if not any(k in r.get("name","") for k in bad_keys)]
                return info
            except Exception as e:
                return CharacterInfo(name=name, description=f"[提取失败: {e}]")

    tasks = [_extract_one(n, m) for n, m in major_chars]
    infos = await asyncio.gather(*tasks)

    # Step 3: 去重与合并
    final_chars = {}
    for c in infos:
        key = c.name.strip()
        if key not in final_chars:
            final_chars[key] = c
        else:
            exist = final_chars[key]
            if len(c.description) > len(exist.description):
                exist.description = c.description
            if not exist.personality and c.personality:
                exist.personality = c.personality
            if not exist.appearance and c.appearance:
                exist.appearance = c.appearance
            if not exist.speech_pattern and c.speech_pattern:
                exist.speech_pattern = c.speech_pattern
            if not exist.first_message and c.first_message:
                exist.first_message = c.first_message
            for field in ["aliases", "source_works", "likes", "dislikes", "habits", "message_examples"]:
                old_list = getattr(exist, field)
                for item in getattr(c, field):
                    if item and item not in old_list:
                        old_list.append(item)
            exist_rels = {r.get("name") for r in exist.relations if isinstance(r, dict)}
            for r in c.relations:
                if isinstance(r, dict) and r.get("name") not in exist_rels:
                    exist.relations.append(r)

    deduped = list(final_chars.values())

    # Step 4: 组装
    return {
        "title": title,
        "total_chars": len(text),
        "chunks": len(chunks),
        "characters_found": len(deduped),
        "minor_characters": minor_count,
        "characters": [c.model_dump() for c in deduped],
        "roster_raw": {k: {"aliases": v["aliases"], "major": v["major"]} for k, v in roster.items()},
    }


# ============ 角色卡完整生成 ============

async def synthesize_description(info: CharacterInfo) -> dict:
    """合成顶级社区标准的角色描述"""
    system = """你是 SillyTavern 角色卡描述专家。根据角色信息合成高质量描述。
输出严格 JSON，每条都要具体、可感，不要空洞形容词。

{
  "description_synth": "1200-2000字 PList 格式描述",
  "personality_profile": "400-800字性格分析",
  "scenario_context": "200-350字具体场景（时间/地点/氛围/冲突）",
  "appearance": "100-300字外貌",
  "speech_pattern": "80-200字说话方式",
  "skills_abilities": "150-400字能力与限制",
  "relations": "至少3个关系的详细描述",
  "likes": "5个以上喜好",
  "dislikes": "5个以上厌恶",
  "habits_quirks": "4个以上习惯",
  "goal": "100-200字（含恐惧）",
  "alternate_greetings": ["5条不同情境开场，每条100-200字"]
}"""

    prompt = f"""角色名：{info.name}
别名：{', '.join(info.aliases)}
出处：{', '.join(info.source_works)}
概述：{info.description}
性格：{info.personality}
外貌：{info.appearance}
说话方式：{info.speech_pattern}
关系：{json.dumps(info.relations, ensure_ascii=False)}
喜好：{', '.join(info.likes)}
厌恶：{', '.join(info.dislikes)}
习惯：{', '.join(info.habits)}
目标：{info.goal}"""

    result = await call_llm_json(prompt, system=system, max_tokens=8192)
    return _safe_json(result, {})


async def generate_dialogue(info: CharacterInfo, scenario: str = "") -> str:
    """生成 SillyTavern 格式对话示例"""
    system = """你是对话生成专家。为角色卡生成自然、符合角色性格的对话示例。
格式：
<START>
{{user}}: 用户说的话
{{char}}: 角色的回复（150-300字，包含动作、表情、内心活动）
<START>
...

生成 4-6 组对话，展示角色不同情绪面和互动方式。"""

    scenario_text = scenario or info.scenario or "在一个日常场景中"
    prompt = f"""角色：{info.name}
性格：{info.personality}
说话方式：{info.speech_pattern}
场景：{scenario_text}

请生成对话示例。"""

    return await call_llm(prompt, system=system, max_tokens=4096)


async def generate_character_card(name: str, raw_text: str, source: str = "") -> CharacterCard:
    """完整流程：从原始文本生成角色卡"""
    # 1. 提取角色信息
    info = await extract_character_info(name, raw_text, source)

    # 2. 合成描述
    synth = await synthesize_description(info)

    # 3. 生成对话
    scenario = synth.get("scenario_context", "") or info.scenario
    dialogue = await generate_dialogue(info, scenario)

    # 4. 组装角色卡
    description_parts = []
    if synth.get("description_synth"):
        description_parts.append(synth["description_synth"])
    if synth.get("personality_profile"):
        description_parts.append(f"\n[Personality]\n{synth['personality_profile']}")
    if synth.get("appearance"):
        description_parts.append(f"\n[Appearance]\n{synth['appearance']}")
    if synth.get("speech_pattern"):
        description_parts.append(f"\n[Speech Pattern]\n{synth['speech_pattern']}")
    if synth.get("skills_abilities"):
        description_parts.append(f"\n[Abilities]\n{synth['skills_abilities']}")

    greetings = synth.get("alternate_greetings", [])
    first_mes = greetings[0] if greetings else info.first_message

    return CharacterCard(
        name=info.name,
        description="\n".join(description_parts),
        personality=synth.get("personality_profile", info.personality),
        scenario=scenario,
        first_mes=first_mes,
        mes_example=dialogue,
        creator_notes=f"来源: {source}\n{synth.get('goal', '')}",
        tags=[source] if source else [],
    )


# ============ 保留原有：单角色提取 / 关系 / 世界观 / 世界书 ============

async def extract_character_info(name: str, raw_text: str, source: str = "") -> CharacterInfo:
    """从原始文本中提取单个角色的结构化信息（兼容旧接口）"""
    return await extract_character_deep(name, [], raw_text[:60000], source)


async def extract_relations(text: str) -> list:
    """从文本中提取隐式角色关系"""
    system = """你是角色关系分析专家。从文本中提取所有角色关系，包括隐含的（暗恋、曾为敌后为友等）。
输出 JSON 数组：
[{"character_a": "角色A", "character_b": "角色B", "relation": "关系类型", "detail": "具体描述", "confidence": "high/medium/low"}]"""

    prompt = f"请分析以下文本中的角色关系：\n\n{text[:20000]}"
    result = await call_llm_json(prompt, system=system, max_tokens=4096)
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return result.get("relations", []) or []
    return []


async def extract_world_concepts(text: str) -> dict:
    """从文本中提取世界观概念"""
    system = """你是世界观分析专家。从文本中提取世界观设定概念，输出严格 JSON：
{
  "currency": ["货币"],
  "food": ["食物/饮品"],
  "language": ["语言/文字"],
  "religion": ["宗教/信仰"],
  "customs": ["习俗/节日"],
  "creatures": ["虚构生物"],
  "geography": ["地名/地理"],
  "organizations": ["组织/势力"],
  "technology": ["科技/魔法体系"]
}"""

    prompt = f"请从以下文本中提取世界观概念：\n\n{text[:20000]}"
    result = await call_llm_json(prompt, system=system, max_tokens=4096)
    return _safe_json(result, {})


async def write_lorebook_entry(concept: str, context: str = "") -> dict:
    """生成世界书条目"""
    system = """你是 SillyTavern 世界书条目专家。根据概念生成详细的世界书条目，输出严格 JSON：
{
  "title": "条目标题",
  "content": "200-5000字的详细条目内容（markdown 格式）",
  "keywords": ["触发关键词"],
  "category": "人物/地点/组织/物品/事件/概念"
}"""

    prompt = f"""概念：{concept}
上下文：{context[:8000] if context else '无'}

内容要详实，适合作为 AI 角色扮演的世界观参考。"""

    result = await call_llm_json(prompt, system=system, max_tokens=4096)
    return _safe_json(result, {"error": "生成失败"})


async def generate_lorebook(text: str, source_name: str = "") -> list:
    """从文本自动生成完整世界书（多条目）"""
    system = """你是世界书生成专家。从给定文本识别所有值得记录的世界观概念，为每个概念生成一个世界书条目。
输出 JSON 数组：
[
  {
    "title": "条目标题",
    "content": "详细内容（至少 100 字）",
    "keywords": ["触发词"],
    "category": "人物/地点/组织/物品/事件/概念"
  }
]

识别范围：地名、组织、种族、魔法/科技体系、历史事件、重要物品、习俗节日等。"""

    prompt = f"""来源：{source_name}

---
{text[:30000]}
---

请提取世界观概念并生成世界书条目。"""

    result = await call_llm_json(prompt, system=system, max_tokens=8192)
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return result.get("entries", []) or []
    return []
