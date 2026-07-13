"""卡片库路由 - 本地SQLite存储"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from ..services.database import (
    create_card,
    get_card,
    list_cards,
    update_card,
    delete_card,
    create_lorebook,
    get_lorebook,
    list_lorebooks,
    add_lorebook_entry,
    delete_lorebook,
)

router = APIRouter(prefix="/api/library", tags=["library"])


# === 请求模型 ===

class CardCreateRequest(BaseModel):
    name: str
    source: str = ""
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
    image_url: str = ""


class CardUpdateRequest(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    scenario: Optional[str] = None
    first_mes: Optional[str] = None
    mes_example: Optional[str] = None
    creator_notes: Optional[str] = None
    system_prompt: Optional[str] = None
    post_history_instructions: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None


class LorebookCreateRequest(BaseModel):
    name: str
    description: str = ""


class LorebookEntryRequest(BaseModel):
    title: str
    content: str = ""
    keywords: List[str] = []
    category: str = ""


# === 角色卡端点 ===

@router.post("/cards")
async def api_create_card(req: CardCreateRequest):
    """创建角色卡"""
    card = create_card(req.model_dump())
    return {"status": "ok", "card": card}


@router.get("/cards")
async def api_list_cards(
    search: str = Query("", description="搜索关键词"),
    source: str = Query("", description="数据源筛选"),
    tag: str = Query("", description="标签筛选"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """列出角色卡"""
    return list_cards(search=search, source=source, tag=tag, page=page, per_page=per_page)


@router.get("/cards/{card_id}")
async def api_get_card(card_id: int):
    """获取角色卡详情"""
    card = get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="角色卡不存在")
    return {"status": "ok", "card": card}


@router.put("/cards/{card_id}")
async def api_update_card(card_id: int, req: CardUpdateRequest):
    """更新角色卡"""
    card = update_card(card_id, req.model_dump(exclude_none=True))
    if not card:
        raise HTTPException(status_code=404, detail="角色卡不存在")
    return {"status": "ok", "card": card}


@router.delete("/cards/{card_id}")
async def api_delete_card(card_id: int):
    """删除角色卡"""
    if not delete_card(card_id):
        raise HTTPException(status_code=404, detail="角色卡不存在")
    return {"status": "ok", "message": "已删除"}


# === 世界书端点 ===

@router.post("/lorebooks")
async def api_create_lorebook(req: LorebookCreateRequest):
    """创建世界书"""
    lb = create_lorebook(req.name, req.description)
    return {"status": "ok", "lorebook": lb}


@router.get("/lorebooks")
async def api_list_lorebooks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """列出世界书"""
    return list_lorebooks(page=page, per_page=per_page)


@router.get("/lorebooks/{lorebook_id}")
async def api_get_lorebook(lorebook_id: int):
    """获取世界书详情（含条目）"""
    lb = get_lorebook(lorebook_id)
    if not lb:
        raise HTTPException(status_code=404, detail="世界书不存在")
    return {"status": "ok", "lorebook": lb}


@router.post("/lorebooks/{lorebook_id}/entries")
async def api_add_entry(lorebook_id: int, req: LorebookEntryRequest):
    """添加世界书条目"""
    lb = get_lorebook(lorebook_id)
    if not lb:
        raise HTTPException(status_code=404, detail="世界书不存在")
    entry = add_lorebook_entry(lorebook_id, req.model_dump())
    return {"status": "ok", "entry": entry}


@router.delete("/lorebooks/{lorebook_id}")
async def api_delete_lorebook(lorebook_id: int):
    """删除世界书"""
    if not delete_lorebook(lorebook_id):
        raise HTTPException(status_code=404, detail="世界书不存在")
    return {"status": "ok", "message": "已删除"}
