"""Danbooru搜索服务 - 角色标签/外貌描述标签"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult

DANBOORU_API = "https://danbooru.donmai.us"


async def search_danbooru(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索Danbooru角色标签"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Danbooru标签搜索
            resp = await client.get(
                f"{DANBOORU_API}/tags.json",
                params={
                    "search[name_matches]: " + query,
                    "limit": limit,
                    "search[order]": "count",
                },
                headers={"User-Agent": "NexusFree/0.4.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for tag in data[:limit]:
                        results.append(
                            CharacterSearchResult(
                                name=tag.get("name", query).replace("_", " "),
                                source="danbooru",
                                url=f"{DANBOORU_API}/wiki_pages/{tag.get('name', '')}",
                                summary=f"Danbooru标签: {tag.get('name', '')} (相关作品: {tag.get('post_count', 0)})",
                            )
                        )
        except Exception as e:
            pass

    # 也搜wiki页面获取角色描述
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            wiki_query = query.lower().replace(" ", "_")
            resp = await client.get(
                f"{DANBOORU_API}/wiki_pages/{wiki_query}.json",
                headers={"User-Agent": "NexusFree/0.4.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                body = data.get("body", "")[:500]
                if body:
                    results.append(
                        CharacterSearchResult(
                            name=query,
                            source="danbooru:wiki",
                            url=f"{DANBOORU_API}/wiki_pages/{wiki_query}",
                            summary=body,
                        )
                    )
        except Exception:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="danbooru",
                url=f"{DANBOORU_API}/posts?tags={query}",
                summary=f"Danbooru搜索: {query}",
            )
        )
    return results
