"""AI生成路由 - 完整功能"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ..services.analyzer import (
    extract_character_info,
    extract_relations,
    extract_world_concepts,
    generate_character_card,
    synthesize_description,
    generate_dialogue,
    write_lorebook_entry,
    generate_lorebook,
    process_long_text,
)
from ..models.character import CharacterCard

router = APIRouter(prefix="/api", tags=["generate"])


# === 请求模型 ===

class GenerateRequest(BaseModel):
    """生成请求"""
    name: str
    source_data: Optional[str] = None
    source: str = ""
    ai_enabled: bool = True


class CardExportRequest(BaseModel):
    """角色卡导出请求"""
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""


class RelationsRequest(BaseModel):
    """关系提取请求"""
    text: str


class WorldConceptsRequest(BaseModel):
    """世界观提取请求"""
    text: str


class LorebookEntryRequest(BaseModel):
    """世界书条目请求"""
    concept: str
    context: str = ""


class LorebookRequest(BaseModel):
    """世界书生成请求"""
    text: str
    source_name: str = ""


class LongTextRequest(BaseModel):
    """长文炼化请求"""
    text: str
    title: str = ""


# === AI 生成端点 ===

@router.post("/generate")
async def generate_character(req: GenerateRequest):
    """AI生成角色信息 - 从原始文本提取并合成"""
    if not req.source_data:
        raise HTTPException(status_code=400, detail="缺少 source_data 原始文本")

    try:
        card = await generate_character_card(
            name=req.name,
            raw_text=req.source_data,
            source=req.source,
        )
        return {
            "status": "ok",
            "card": card.model_dump(),
            "format": "SillyTavern V2",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/extract/relations")
async def api_extract_relations(req: RelationsRequest):
    """从文本中提取角色关系"""
    try:
        relations = await extract_relations(req.text)
        return {"status": "ok", "relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/world-concepts")
async def api_extract_world_concepts(req: WorldConceptsRequest):
    """从文本中提取世界观概念"""
    try:
        concepts = await extract_world_concepts(req.text)
        return {"status": "ok", "concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === 世界书端点 ===

@router.post("/lorebook/entry")
async def api_lorebook_entry(req: LorebookEntryRequest):
    """生成单个世界书条目"""
    try:
        entry = await write_lorebook_entry(req.concept, req.context)
        return {"status": "ok", "entry": entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lorebook/generate")
async def api_generate_lorebook(req: LorebookRequest):
    """从文本自动生成完整世界书"""
    try:
        entries = await generate_lorebook(req.text, req.source_name)
        return {
            "status": "ok",
            "entries": entries,
            "count": len(entries),
            "format": "SillyTavern Lorebook",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === 长文炼化端点 ===

@router.post("/long-text")
async def api_long_text(req: LongTextRequest):
    """长文炼化 - 从长文本生成角色信息和世界书"""
    try:
        result = await process_long_text(req.text, req.title)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === 导出端点 ===

@router.post("/export/card")
async def export_card(req: CardExportRequest):
    """导出SillyTavern V2角色卡"""
    card = {
        "name": req.name,
        "description": req.description,
        "personality": req.personality,
        "scenario": req.scenario,
        "first_mes": req.first_mes,
        "mes_example": req.mes_example,
        "creator_notes": "由 Nexus Free 生成",
        "system_prompt": "",
        "post_history_instructions": "",
        "tags": [],
        "creator": "Nexus Free",
        "character_version": "2.0",
    }
    return {"status": "ok", "card": card, "format": "SillyTavern V2"}
