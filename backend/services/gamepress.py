"""GamePress搜索服务 - 游戏攻略/角色评测"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult

GAMEPRESS_SITES = {
    "arknights": "https://gamepress.gg/arknights",
    "genshin": "https://gamepress.gg/genshinimpact",
    "fgo": "https://gamepress.gg/grandorder",
    "epic7": "https://gamepress.gg/epicseven",
}


async def search_gamepress(query: str, game: str = "arknights", limit: int = 5) -> List[CharacterSearchResult]:
    """搜索GamePress"""
    results = []
    base_url = GAMEPRESS_SITES.get(game, f"https://gamepress.gg/{game}")

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # GamePress搜索
            resp = await client.get(
                f"{base_url}/search-content",
                params={"search": query, "type": "operator"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("results", [])
                for item in items[:limit]:
                    title = item.get("title", query)
                    results.append(
                        CharacterSearchResult(
                            name=title,
                            source=f"gamepress:{game}",
                            url=f"{base_url}{item.get('url', '')}",
                            summary=item.get("summary", "")[:200],
                        )
                    )
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source=f"gamepress:{game}",
                url=f"{base_url}/search?search={query}",
                summary=f"GamePress搜索: {query}",
            )
        )
    return results
