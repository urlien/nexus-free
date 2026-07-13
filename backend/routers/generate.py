"""AI生成路由"""
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
)
from ..models.character import CharacterCard

router = APIRouter(prefix="/api", tags=["generate"])


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
