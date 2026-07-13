"""PRTS Wiki 搜索服务 - 明日方舟专用"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

PRTS_API = "https://prts.wiki/api.php"
PRTS_WIKI_URL = "https://prts.wiki/w/"


async def search_prts(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 PRTS Wiki（明日方舟）"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # opensearch 搜索
            resp = await client.get(
                PRTS_API,
                params={
                    "action": "opensearch",
                    "search": query,
                    "limit": limit,
                    "namespace": 0,
                    "format": "json",
                },
            )
            data = resp.json()
            names = data[1] if len(data) > 1 else []
            urls = data[3] if len(data) > 3 else []

            for i, name in enumerate(names):
                results.append(
                    CharacterSearchResult(
                        name=name,
                        source="prts",
                        url=urls[i] if i < len(urls) else f"{PRTS_WIKI_URL}{name}",
                        summary=f"明日方舟角色: {name}",
                    )
                )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="prts", summary=f"PRTS搜索出错: {str(e)}"
                )
            )
    return results


async def get_prts_character(character_name: str) -> Optional[dict]:
    """从 PRTS Wiki 获取角色详情（完整页面文本）"""
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            # 获取页面内容
            resp = await client.get(
                PRTS_API,
                params={
                    "action": "query",
                    "titles": character_name,
                    "prop": "extracts|pageimages|links|categories",
                    "exintro": False,
                    "explaintext": True,
                    "format": "json",
                },
            )
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if page_id != "-1":
                    return {
                        "name": page_data.get("title", character_name),
                        "extract": page_data.get("extract", ""),
                        "image": page_data.get("thumbnail", {}).get("source"),
                        "url": f"{PRTS_WIKI_URL}{character_name}",
                        "source": "prts",
                    }
        except Exception as e:
            print(f"PRTS获取详情错误: {e}")
    return None


async def get_prts_voice(character_name: str) -> Optional[str]:
    """获取角色语音文本（明日方舟特色）"""
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(
                PRTS_API,
                params={
                    "action": "parse",
                    "page": f"{character_name}/语音记录",
                    "prop": "wikitext",
                    "format": "json",
                },
            )
            data = resp.json()
            wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
            return wikitext[:8000] if wikitext else None
        except Exception:
            return None
