"""NGA搜索服务 - 玩家社区讨论/考据"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult


async def search_nga(query: str, game: str = "arknights", limit: int = 5) -> List[CharacterSearchResult]:
    """搜索NGA论坛
    
    game: arknights(明日方舟), genshin(原神), sr(星穹铁道)
    """
    results = []
    forum_ids = {
        "arknights": "586",
        "genshin": "753",
        "sr": "829",
    }
    fid = forum_ids.get(game, "")

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://bbs.nga.cn/api.php",
                params={
                    "action": "search",
                    "q": query,
                    "fid": fid,
                    "limit": limit,
                    "output": "json",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://bbs.nga.cn/",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("result", {}).get("data", [])
                if isinstance(items, list):
                    for item in items[:limit]:
                        results.append(
                            CharacterSearchResult(
                                name=item.get("title", query)[:50],
                                source=f"nga:{game}",
                                url=f"https://bbs.nga.cn/read.php?tid={item.get('tid', '')}",
                                summary=item.get("subject", "")[:200],
                            )
                        )
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source=f"nga:{game}",
                url=f"https://bbs.nga.cn/search.php?q={query}",
                summary=f"NGA搜索: {query}",
            )
        )
    return results
