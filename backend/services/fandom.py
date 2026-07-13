"""Fandom Wiki 搜索服务"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult


async def search_fandom(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索Fandom Wiki"""
    results = []
    
    # Fandom搜索API
    search_url = f"https://{{wiki_name}}.fandom.com/api.php"
    
    # 先用通用搜索找wiki
    wiki_search_url = "https://www.fandom.com/api/v1/ContentSearch/list"
    params = {
        "query": query,
        "limit": limit,
        "lang": "en"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 搜索wiki
            resp = await client.get(
                "https://www.fandom.com",
                params={"s": query},
                timeout=10
            )
            # 简化：直接返回搜索结果
            results.append(CharacterSearchResult(
                name=query,
                source="fandom",
                url=f"https://www.fandom.com/search?q={query}",
                summary=f"在Fandom搜索 '{query}'"
            ))
        except Exception as e:
            print(f"Fandom搜索错误: {e}")
    
    return results


async def get_fandom_character(wiki_name: str, character_name: str) -> Optional[dict]:
    """从Fandom Wiki获取角色详情"""
    url = f"https://{wiki_name}.fandom.com/api.php"
    params = {
        "action": "query",
        "titles": character_name,
        "prop": "extracts|pageimages|links",
        "exintro": True,
        "explaintext": True,
        "format": "json",
        "origin": "*"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    return {
                        "name": page_data.get("title", character_name),
                        "extract": page_data.get("extract", ""),
                        "image": page_data.get("thumbnail", {}).get("source"),
                        "url": f"https://{wiki_name}.fandom.com/wiki/{character_name}"
                    }
        except Exception as e:
            print(f"Fandom获取详情错误: {e}")
    
    return None
