"""Pixiv搜索服务 - 角色标签/同人描述"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult


async def search_pixiv(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索Pixiv角色标签"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Pixiv标签搜索（公开API）
            resp = await client.get(
                "https://www.pixiv.net/ajax/search/artworks/",
                params={
                    "word": query,
                    "order": "popular_d",
                    "mode": "all",
                    "p": 1,
                    "s_mode": "s_tag",
                    "type": "all",
                    "lang": "zh",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://www.pixiv.net/",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                tags_data = data.get("body", {}).get("relatedTags", {}).get("tags", [])
                for tag in tags_data[:limit]:
                    results.append(
                        CharacterSearchResult(
                            name=tag.get("tag", query),
                            source="pixiv",
                            url=f"https://www.pixiv.net/tags/{tag.get('tag', query)}/artworks",
                            summary=f"Pixiv标签: {tag.get('tag', query)} (翻译: {tag.get('translation', '')})",
                        )
                    )
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="pixiv",
                url=f"https://www.pixiv.net/tags/{query}/artworks",
                summary=f"Pixiv标签搜索: {query}",
            )
        )
    return results
