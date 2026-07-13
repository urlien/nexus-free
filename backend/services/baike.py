"""百度百科搜索服务"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

BAIKE_API = "https://baike.baidu.com/api/openapi"


async def search_baike(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索百度百科"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # 百度百科搜索接口
            resp = await client.get(
                f"{BAIKE_API}/SearchBox/search",
                params={"query": query, "limit": limit, "format": "json"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("result", {}).get("search_list", [])
                for item in items[:limit]:
                    results.append(
                        CharacterSearchResult(
                            name=item.get("title", query),
                            source="baike",
                            url=f"https://baike.baidu.com{item.get('url', '')}",
                            summary=item.get("abstract", "")[:200],
                        )
                    )
        except Exception as e:
            pass

    # 回退：直接构造链接
    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="baike",
                url=f"https://baike.baidu.com/item/{query}",
                summary=f"百度百科: {query}",
            )
        )
    return results


async def get_baike_content(title: str) -> Optional[dict]:
    """获取百度百科页面内容"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"https://baike.baidu.com/item/{title}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                text = resp.text
                # 提取简介
                import re
                abstract = re.search(r'class="lemma-summary[^"]*"[^>]*>(.*?)</div>', text, re.DOTALL)
                abstract_text = re.sub(r'<[^>]+>', '', abstract.group(1)).strip() if abstract else ""
                return {
                    "name": title,
                    "abstract": abstract_text[:2000],
                    "url": f"https://baike.baidu.com/item/{title}",
                    "source": "baike",
                }
        except Exception as e:
            print(f"百度百科获取错误: {e}")
    return None
