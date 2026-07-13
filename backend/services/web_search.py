"""通用网页搜索服务 - 兜底方案"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult


async def search_web(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """通用网页搜索（使用 DuckDuckGo Lite）"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # 使用 DuckDuckGo Lite 版（无需 API key）
            resp = await client.get(
                "https://lite.duckduckgo.com/lite/",
                params={"q": f"{query} 角色 性格 设定"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            text = resp.text

            # 简单解析搜索结果
            import re
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*class="result-link"[^>]*>([^<]+)</a>', text)
            snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', text, re.DOTALL)

            for i, (url, title) in enumerate(links[:limit]):
                snippet = snippets[i].strip() if i < len(snippets) else ""
                snippet = re.sub(r'<[^>]+>', '', snippet)  # 去HTML标签
                results.append(
                    CharacterSearchResult(
                        name=title.strip(),
                        source="web",
                        url=url,
                        summary=snippet[:200],
                    )
                )

        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="web", summary=f"网页搜索出错: {str(e)}"
                )
            )

    # 如果没搜到，至少返回一个
    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="web",
                summary=f"未找到关于「{query}」的网页结果",
            )
        )

    return results
