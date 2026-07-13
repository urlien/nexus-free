"""B站 BWIKI 搜索服务 - 国产手游数据"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

BWIKI_API = "https://wiki.biligame.com"


async def search_bwiki(query: str, game: str = "arknights", limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 B站 BWIKI
    
    支持的游戏 wiki:
    - arknights: 明日方舟
    - genshin: 原神
    - sr: 崩坏：星穹铁道
    - ba: 蔚蓝档案
    - pcr: 公主连结
    """
    results = []
    wiki_url = f"{BWIKI_API}/{game}/api.php"

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                wiki_url,
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
                        source=f"bwiki:{game}",
                        url=urls[i] if i < len(urls) else "",
                        summary=f"[{game}] {name}",
                    )
                )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source=f"bwiki:{game}", summary=f"BWIKI搜索出错: {str(e)}"
                )
            )
    return results


async def get_bwiki_character(character_name: str, game: str = "arknights") -> Optional[dict]:
    """从 BWIKI 获取角色详情"""
    wiki_url = f"{BWIKI_API}/{game}/api.php"

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(
                wiki_url,
                params={
                    "action": "query",
                    "titles": character_name,
                    "prop": "extracts|pageimages",
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
                        "url": f"{BWIKI_API}/{game}/{character_name}",
                        "source": f"bwiki:{game}",
                    }
        except Exception as e:
            print(f"BWIKI获取详情错误: {e}")
    return None
