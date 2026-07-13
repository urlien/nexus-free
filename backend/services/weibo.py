"""微博搜索服务 - 超话讨论/同人创作"""
import httpx
from typing import List
from ..models.character import CharacterSearchResult


async def search_weibo(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索微博超话/话题"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # 微博搜索
            resp = await client.get(
                "https://m.weibo.cn/api/container/getIndex",
                params={
                    "containerid": f"100103type=1&q={query}",
                    "page_type": "searchall",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
                    "Referer": "https://m.weibo.cn/",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                cards = data.get("data", {}).get("cards", [])
                for card in cards:
                    if card.get("card_type") == 9:
                        mblog = card.get("mblog", {})
                        text = mblog.get("text", "")
                        # 去HTML标签
                        import re
                        clean_text = re.sub(r'<[^>]+>', '', text)[:200]
                        if clean_text:
                            results.append(
                                CharacterSearchResult(
                                    name=mblog.get("user", {}).get("screen_name", query),
                                    source="weibo",
                                    url=f"https://m.weibo.cn/detail/{mblog.get('id', '')}",
                                    summary=clean_text,
                                )
                            )
                    if len(results) >= limit:
                        break
        except Exception as e:
            pass

    if not results:
        results.append(
            CharacterSearchResult(
                name=query,
                source="weibo",
                url=f"https://s.weibo.com/weibo?q={query}",
                summary=f"微博搜索: {query}",
            )
        )
    return results
