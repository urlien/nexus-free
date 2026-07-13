"""TV Tropes搜索服务 - 角色trope标签/性格模式分析"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult

TROPES_API = "https://tvtropes.org/pmwiki"


async def search_tvtropes(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索TV Tropes"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{TROPES_API}/search_term.php",
                params={"search": query, "search_type": "article"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                text = resp.text
                import re
                # 解析搜索结果
                links = re.findall(r'<a href="([^"]*pmwiki\.php/[^"]*)"[^>]*>([^<]+)</a>', text)
                for url, title in links[:limit]:
                    results.append(
                        CharacterSearchResult(
                            name=title,
                            source="tvtropes",
                            url=url if url.startswith("http") else f"https://tvtropes.org{url}",
                            summary=f"TV Trope: {title}",
                        )
                    )
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="tvtropes",
                url=f"https://tvtropes.org/pmwiki/search_result.php?q={query}",
                summary=f"TV Tropes搜索: {query}",
            )
        )
    return results


async def get_tvtropes_page(path: str) -> Optional[dict]:
    """获取TV Tropes页面的trope列表"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                path,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            if resp.status_code == 200:
                import re
                text = resp.text
                # 提取trope标签
                tropes = re.findall(r'<a href="/pmwiki/pmwiki\.php/([^"]*)"[^>]*>([^<]+)</a>', text)
                trope_list = [t[1] for t in tropes if "/" in t[0] and t[1] not in ("Main", "Home", "Tropes")]
                return {
                    "tropes": list(set(trope_list))[:30],
                    "url": path,
                    "source": "tvtropes",
                }
        except Exception as e:
            print(f"TV Tropes获取错误: {e}")
    return None
