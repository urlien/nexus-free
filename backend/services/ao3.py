"""AO3搜索服务 - 同人作品标签/关系分析"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult

AO3_API = "https://archiveofourown.org"


async def search_ao3(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索AO3角色标签"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # AO3标签搜索
            resp = await client.get(
                f"{AO3_API}/tags/search",
                params={
                    "query": query,
                    "type": "Character",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "text/html",
                },
            )
            if resp.status_code == 200:
                text = resp.text
                import re
                # 解析标签结果
                tags = re.findall(r'<a href="/tags/([^"]*)"[^>]*>([^<]+)</a>', text)
                for tag_path, tag_name in tags[:limit]:
                    if "characters" in tag_path.lower() or query.lower() in tag_name.lower():
                        results.append(
                            CharacterSearchResult(
                                name=tag_name,
                                source="ao3",
                                url=f"{AO3_API}/tags/{tag_path}",
                                summary=f"AO3角色标签: {tag_name}",
                            )
                        )
        except Exception as e:
            pass

    # 搜索作品
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{AO3_API}/works/search",
                params={
                    "work_search[query]": query,
                    "work_search[sort_column]": "kudos_count",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "text/html",
                },
            )
            if resp.status_code == 200:
                text = resp.text
                import re
                # 提取作品标题和关系标签
                works = re.findall(r'<h4[^>]*>.*?<a[^>]*>([^<]+)</a>.*?</h4>', text, re.DOTALL)
                relationships = re.findall(r'<li[^>]*class="relationships"[^>]*>.*?<a[^>]*>([^<]+)</a>', text, re.DOTALL)
                for rel in relationships[:3]:
                    results.append(
                        CharacterSearchResult(
                            name=rel.strip(),
                            source="ao3:relationship",
                            url=f"{AO3_API}/works/search?work_search[query]={query}",
                            summary=f"AO3关系标签: {rel.strip()}",
                        )
                    )
        except Exception:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="ao3",
                url=f"{AO3_API}/works/search?work_search[query]={query}",
                summary=f"AO3搜索: {query}",
            )
        )
    return results
