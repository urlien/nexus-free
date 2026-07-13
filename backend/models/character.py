"""角色数据模型"""
from pydantic import BaseModel
from typing import Optional, List


class CharacterSearchResult(BaseModel):
    """搜索结果"""
    name: str
    source: str  # fandom, moegirl, prts, etc.
    url: Optional[str] = None
    summary: Optional[str] = None
    image: Optional[str] = None


class CharacterInfo(BaseModel):
    """角色详细信息"""
    name: str
    aliases: List[str] = []
    source_works: List[str] = []
    description: str = ""
    personality: str = ""
    appearance: str = ""
    speech_pattern: str = ""
    relations: List[dict] = []
    likes: List[str] = []
    dislikes: List[str] = []
    habits: List[str] = []
    goal: str = ""
    scenario: str = ""
    first_message: str = ""
    message_examples: List[str] = []


class CharacterCard(BaseModel):
    """SillyTavern V2 角色卡"""
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    creator_notes: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    tags: List[str] = []
    creator: str = "Nexus Free"
    character_version: str = "2.0"
