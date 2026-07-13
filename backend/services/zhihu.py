"""知乎搜索服务 - 角色分析长文/考据帖"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult


async def search_zhihu(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索知乎相关内容"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # 知乎搜索API（公开）
            resp = await client.get(
                "https://www.zhihu.com/api/v4/search_v3",
                params={
                    "t": "general",
                    "q": f"{query} 角色 分析",
                    "correction": 1,
                    "offset": 0,
                    "limit": limit,
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.zhihu.com/",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    obj = item.get("object", {})
                    if obj.get("type") in ("answer", "article"):
                        title = obj.get("title", "") or obj.get("question", {}).get("title", "")
                        excerpt = obj.get("excerpt", "") or obj.get("content", "")
                        url = obj.get("url", "")
                        if title:
                            results.append(
                                CharacterSearchResult(
                                    name=title[:50],
                                    source="zhihu",
                                    url=url,
                                    summary=excerpt[:200],
                                )
                            )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="zhihu", summary=f"知乎搜索出错: {str(e)}"
                )
            )

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="zhihu",
                url=f"https://www.zhihu.com/search?type=content&q={query}",
                summary=f"知乎搜索: {query}",
            )
        )
    return results
