"""搜索路由 - 18个数据源"""
from fastapi import APIRouter, Query
from typing import List
from ..models.character import CharacterSearchResult

# === 原有8个 ===
from ..services.fandom import search_fandom
from ..services.moegirl import search_moegirl
from ..services.prts import search_prts
from ..services.bwiki import search_bwiki
from ..services.anilist import search_anilist
from ..services.bangumi import search_bangumi
from ..services.wikidata import search_wikidata
from ..services.web_search import search_web

# === 新增10个 ===
from ..services.baike import search_baike
from ..services.zhihu import search_zhihu
from ..services.nga import search_nga
from ..services.gamepress import search_gamepress
from ..services.tvtropes import search_tvtropes
from ..services.pixiv import search_pixiv
from ..services.danbooru import search_danbooru
from ..services.weibo import search_weibo
from ..services.ao3 import search_ao3
from ..services.myanimelist import search_myanimelist

router = APIRouter(prefix="/api", tags=["search"])

# 数据源映射
SOURCE_MAP = {
    # 原有8个
    "fandom": search_fandom,
    "moegirl": search_moegirl,
    "prts": search_prts,
    "bwiki": search_bwiki,
    "anilist": search_anilist,
    "bangumi": search_bangumi,
    "wikidata": search_wikidata,
    "web": search_web,
    # 新增10个
    "baike": search_baike,
    "zhihu": search_zhihu,
    "nga": search_nga,
    "gamepress": search_gamepress,
    "tvtropes": search_tvtropes,
    "pixiv": search_pixiv,
    "danbooru": search_danbooru,
    "weibo": search_weibo,
    "ao3": search_ao3,
    "myanimelist": search_myanimelist,
}

ALL_SOURCES = list(SOURCE_MAP.keys())


@router.get("/search")
async def search_characters(
    query: str = Query(..., description="角色名"),
    sources: str = Query("all", description="数据源，逗号分隔，或 'all'"),
):
    """搜索角色 - 18源聚合

    数据源:
    [原有] fandom, moegirl, prts, bwiki, anilist, bangumi, wikidata, web
    [新增] baike, zhihu, nga, gamepress, tvtropes, pixiv, danbooru, weibo, ao3, myanimelist
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
            # 原有8个
            {"id": "fandom", "name": "Fandom Wiki", "desc": "全球最大Wiki平台", "group": "百科"},
            {"id": "moegirl", "name": "萌娘百科", "desc": "中文二次元百科", "group": "百科"},
            {"id": "prts", "name": "PRTS Wiki", "desc": "明日方舟专用", "group": "百科"},
            {"id": "bwiki", "name": "B站BWIKI", "desc": "国产手游数据", "group": "百科"},
            {"id": "anilist", "name": "AniList", "desc": "50万+动漫角色", "group": "百科"},
            {"id": "bangumi", "name": "Bangumi", "desc": "中文ACGN数据库", "group": "百科"},
            {"id": "wikidata", "name": "Wikidata", "desc": "跨平台ID映射", "group": "百科"},
            {"id": "web", "name": "网页搜索", "desc": "通用网页搜索兜底", "group": "通用"},
            # 新增10个
            {"id": "baike", "name": "百度百科", "desc": "中文百科全书", "group": "百科"},
            {"id": "zhihu", "name": "知乎", "desc": "角色分析长文/考据帖", "group": "社区"},
            {"id": "nga", "name": "NGA", "desc": "玩家社区讨论/考据", "group": "社区"},
            {"id": "gamepress", "name": "GamePress", "desc": "游戏攻略/角色评测", "group": "攻略"},
            {"id": "tvtropes", "name": "TV Tropes", "desc": "角色trope标签/性格模式", "group": "分析"},
            {"id": "pixiv", "name": "Pixiv", "desc": "角色标签/同人描述", "group": "创作"},
            {"id": "danbooru", "name": "Danbooru", "desc": "角色标签/外貌描述", "group": "创作"},
            {"id": "weibo", "name": "微博", "desc": "超话讨论/同人创作", "group": "社区"},
            {"id": "ao3", "name": "AO3", "desc": "同人作品标签/关系分析", "group": "创作"},
            {"id": "myanimelist", "name": "MyAnimeList", "desc": "动漫角色数据库", "group": "百科"},
        ]
    }
