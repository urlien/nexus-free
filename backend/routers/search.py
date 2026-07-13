"""搜索路由 - 8个数据源"""
from fastapi import APIRouter, Query
from typing import List
from ..models.character import CharacterSearchResult
from ..services.fandom import search_fandom
from ..services.moegirl import search_moegirl
from ..services.prts import search_prts
from ..services.bwiki import search_bwiki
from ..services.anilist import search_anilist
from ..services.bangumi import search_bangumi
from ..services.wikidata import search_wikidata
from ..services.web_search import search_web

router = APIRouter(prefix="/api", tags=["search"])

# 数据源映射
SOURCE_MAP = {
    "fandom": search_fandom,
    "moegirl": search_moegirl,
    "prts": search_prts,
    "bwiki": search_bwiki,
    "anilist": search_anilist,
    "bangumi": search_bangumi,
    "wikidata": search_wikidata,
    "web": search_web,
}

ALL_SOURCES = list(SOURCE_MAP.keys())


@router.get("/search")
async def search_characters(
    query: str = Query(..., description="角色名"),
    sources: str = Query("all", description="数据源，逗号分隔，或 'all'"),
):
    """搜索角色 - 8源聚合

    数据源: fandom, moegirl, prts, bwiki, anilist, bangumi, wikidata, web
    """
    results = []

    if sources == "all":
        source_list = ALL_SOURCES
    else:
        source_list = [s.strip() for s in sources.split(",")]

    for source in source_list:
        search_fn = SOURCE_MAP.get(source)
        if search_fn:
            try:
                source_results = await search_fn(query)
                results.extend(source_results)
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


@router.get("/sources")
async def list_sources():
    """列出所有可用数据源"""
    return {
        "sources": [
            {"id": "fandom", "name": "Fandom Wiki", "desc": "全球最大Wiki平台"},
            {"id": "moegirl", "name": "萌娘百科", "desc": "中文二次元百科"},
            {"id": "prts", "name": "PRTS Wiki", "desc": "明日方舟专用"},
            {"id": "bwiki", "name": "B站BWIKI", "desc": "国产手游数据"},
            {"id": "anilist", "name": "AniList", "desc": "50万+动漫角色"},
            {"id": "bangumi", "name": "Bangumi", "desc": "中文ACGN数据库"},
            {"id": "wikidata", "name": "Wikidata", "desc": "跨平台ID映射"},
            {"id": "web", "name": "网页搜索", "desc": "通用网页搜索兜底"},
        ]
    }
