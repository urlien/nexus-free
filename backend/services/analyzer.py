"""AI 角色分析管道"""
from .llm import call_llm, call_llm_json
from ..models.character import CharacterInfo, CharacterCard


async def extract_character_info(name: str, raw_text: str, source: str = "") -> CharacterInfo:
    """从原始文本中提取结构化角色信息"""
    system = """你是角色信息提取专家。从给定文本中提取角色的详细信息，输出JSON格式。
严格按以下字段输出，没有信息的字段留空字符串或空数组：
{
  "name": "角色名",
  "aliases": ["别名1", "别名2"],
  "source_works": ["出处作品"],
  "description": "200字以上的角色概述",
  "personality": "性格特征描述",
  "appearance": "外貌描述",
  "speech_pattern": "说话方式/口癖/语速",
  "relations": [{"name": "关系人", "relation": "关系类型", "detail": "具体描述"}],
  "likes": ["喜欢的事物"],
  "dislikes": ["讨厌的事物"],
  "habits": ["习惯/癖好"],
  "goal": "目标/动机/恐惧"
}"""

    prompt = f"""请从以下文本中提取角色「{name}」的信息：

来源：{source}

---
{raw_text[:6000]}
---

请输出JSON格式的角色信息。"""

    result = await call_llm_json(prompt, system=system)

    if "error" in result:
        # 回退：用基本文本作为描述
        return CharacterInfo(
            name=name,
            description=raw_text[:2000],
            source_works=[source] if source else [],
        )

    return CharacterInfo(
        name=result.get("name", name),
        aliases=result.get("aliases", []),
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
    )


async def extract_relations(text: str) -> list:
    """从文本中提取隐式角色关系"""
    system = """你是角色关系分析专家。从文本中提取所有角色关系，包括隐含的（如暗恋、曾为敌后为友等）。
输出JSON数组：
[{"character_a": "角色A", "character_b": "角色B", "relation": "关系类型", "detail": "具体描述", "confidence": "high/medium/low"}]"""

    prompt = f"请分析以下文本中的角色关系：\n\n{text[:5000]}"

    result = await call_llm_json(prompt, system=system)
    return result if isinstance(result, list) else result.get("relations", [])


async def extract_world_concepts(text: str) -> dict:
    """从文本中提取世界观概念"""
    system = """你是世界观分析专家。从文本中提取世界观设定概念。
输出JSON：
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

    prompt = f"请从以下文本中提取世界观概念：\n\n{text[:5000]}"

    return await call_llm_json(prompt, system=system)


async def synthesize_description(info: CharacterInfo) -> dict:
    """合成顶级社区标准的角色描述"""
    system = """你是SillyTavern角色卡描述专家。根据角色信息合成高质量的PLists格式描述。
输出JSON：
{
  "description_synth": "1200-2000字PLists格式描述",
  "personality_profile": "400-800字性格分析",
  "scenario_context": "200-350字具体场景（时间/地点/氛围/冲突）",
  "appearance": "100-300字外貌",
  "speech_pattern": "80-200字说话方式",
  "skills_abilities": "150-400字能力与限制",
  "relations": "至少3个关系的详细描述",
  "likes": "5+个喜好",
  "dislikes": "5+个厌恶",
  "habits_quirks": "4+个习惯",
  "goal": "100-200字（含恐惧）",
  "alternate_greetings": ["5条不同情境开场，每条100-200字"]
}"""

    prompt = f"""请根据以下角色信息合成高质量描述：

角色名：{info.name}
别名：{', '.join(info.aliases)}
出处：{', '.join(info.source_works)}
概述：{info.description}
性格：{info.personality}
外貌：{info.appearance}
说话方式：{info.speech_pattern}
能力：{info.skills_abilities if hasattr(info, 'skills_abilities') else ''}
关系：{info.relations}
喜好：{info.likes}
厌恶：{info.dislikes}
习惯：{info.habits}
目标：{info.goal}"""

    return await call_llm_json(prompt, system=system)


async def generate_dialogue(info: CharacterInfo, scenario: str = "") -> str:
    """生成SillyTavern格式的对话示例"""
    system = """你是对话生成专家。为角色卡生成自然、符合角色性格的对话示例。
格式要求：
<START>
{{user}}: 用户说的话
{{char}}: 角色的回复（150-300字，包含动作、表情、内心活动）
<START>
...

生成4-6组对话，展示角色的不同情绪面和互动方式。"""

    scenario_text = scenario or info.scenario or "在一个日常场景中"
    prompt = f"""角色：{info.name}
性格：{info.personality}
说话方式：{info.speech_pattern}
场景：{scenario_text}

请生成对话示例。"""

    return await call_llm(prompt, system=system)


async def generate_character_card(name: str, raw_text: str, source: str = "") -> CharacterCard:
    """完整流程：从原始文本生成角色卡"""
    # 1. 提取角色信息
    info = await extract_character_info(name, raw_text, source)

    # 2. 合成描述
    synth = await synthesize_description(info)

    # 3. 生成对话
    scenario = synth.get("scenario_context", "")
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

    return CharacterCard(
        name=info.name,
        description="\n".join(description_parts),
        personality=synth.get("personality_profile", info.personality),
        scenario=synth.get("scenario_context", ""),
        first_mes=synth.get("alternate_greetings", [""])[0] if synth.get("alternate_greetings") else "",
        mes_example=dialogue,
        creator_notes=f"来源: {source}\n{synth.get('goal', '')}",
        tags=[source] if source else [],
    )
