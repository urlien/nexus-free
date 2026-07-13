"""萌娘百科搜索服务"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult


async def search_moegirl(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索萌娘百科镜像"""
    results = []
    
    # 萌娘百科openSearch API
    search_url = "https://moegirl.org.cn/api.php"
    params = {
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "namespace": 0,
        "format": "json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(search_url, params=params, timeout=10)
            data = resp.json()
            
            if len(data) >= 4:
                names = data[1]
                descriptions = data[2]
                urls = data[3]
                
                for name, desc, url in zip(names, descriptions, urls):
                    results.append(CharacterSearchResult(
                        name=name,
                        source="moegirl",
                        url=url,
                        summary=desc[:200] if desc else ""
                    ))
        except Exception as e:
            print(f"萌娘百科搜索错误: {e}")
    
    return results


async def get_moegirl_character(character_name: str) -> Optional[dict]:
    """从萌娘百科获取角色详情"""
    url = f"https://moegirl.org.cn/api.php"
    params = {
        "action": "query",
        "titles": character_name,
        "prop": "extracts|pageimages",
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
                        "url": f"https://moegirl.org.cn/{character_name}"
                    }
        except Exception as e:
            print(f"萌娘百科获取详情错误: {e}")
    
    return None
