"""搜索路由"""
from fastapi import APIRouter, Query
from typing import List
from ..models.character import CharacterSearchResult
from ..services.fandom import search_fandom
from ..services.moegirl import search_moegirl

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
async def search_characters(
    query: str = Query(..., description="角色名"),
    sources: str = Query("fandom,moegirl", description="数据源，逗号分隔"),
):
    """搜索角色 - 多源聚合"""
    results = []
    source_list = [s.strip() for s in sources.split(",")]

    for source in source_list:
        try:
            if source == "fandom":
                results.extend(await search_fandom(query))
            elif source == "moegirl":
                results.extend(await search_moegirl(query))
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query,
                    source=source,
                    summary=f"搜索出错: {str(e)}",
                )
            )

    return {
        "query": query,
        "sources": source_list,
        "count": len(results),
        "results": [r.model_dump() for r in results],
    }
