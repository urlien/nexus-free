"""MyAnimeList搜索服务 - 动漫角色数据库"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

MAL_API = "https://api.myanimelist.net/v2"


async def search_myanimelist(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索MyAnimeList角色"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # MAL公开搜索（无需API key的网页搜索）
            resp = await client.get(
                "https://myanimelist.net/search/prefix.json",
                params={
                    "type": "character",
                    "keyword": query,
                    "v": 1,
                },
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("categories", [{}])[0].get("items", [])
                for item in items[:limit]:
                    name = item.get("name", query)
                    url = item.get("url", "")
                    es = item.get("es_name", "")
                    results.append(
                        CharacterSearchResult(
                            name=name,
                            source="myanimelist",
                            url=url,
                            summary=f"MAL角色: {name}" + (f" ({es})" if es else ""),
                            image=item.get("image_url", ""),
                        )
                    )
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="myanimelist",
                url=f"https://myanimelist.net/character.php?q={query}",
                summary=f"MAL搜索: {query}",
            )
        )
    return results


async def get_mal_character(character_id: int) -> Optional[dict]:
    """获取MAL角色详情"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"https://myanimelist.net/character/{character_id}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                import re
                text = resp.text
                # 提取角色描述
                desc_match = re.search(r'<div[^>]*class="[^"]*character[^"]*"[^>]*>(.*?)</div>', text, re.DOTALL)
                desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:2000] if desc_match else ""
                return {
                    "description": desc,
                    "url": f"https://myanimelist.net/character/{character_id}",
                    "source": "myanimelist",
                }
        except Exception as e:
            print(f"MAL获取错误: {e}")
    return None
