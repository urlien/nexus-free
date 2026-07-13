"""Wikidata 搜索服务 - 跨平台ID映射"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

WIKIDATA_API = "https://www.wikidata.org/w/api.php"


async def search_wikidata(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 Wikidata 实体"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                WIKIDATA_API,
                params={
                    "action": "wbsearchentities",
                    "search": query,
                    "language": "zh",
                    "limit": limit,
                    "format": "json",
                },
            )
            data = resp.json()
            entities = data.get("search", [])

            for entity in entities:
                results.append(
                    CharacterSearchResult(
                        name=entity.get("label", query),
                        source="wikidata",
                        url=entity.get("url", ""),
                        summary=entity.get("description", ""),
                    )
                )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="wikidata", summary=f"Wikidata搜索出错: {str(e)}"
                )
            )
    return results


async def get_wikidata_entity(entity_id: str) -> Optional[dict]:
    """获取 Wikidata 实体详情（含跨平台链接）"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                WIKIDATA_API,
                params={
                    "action": "wbgetentities",
                    "ids": entity_id,
                    "languages": "zh|en",
                    "format": "json",
                },
            )
            data = resp.json()
            entity = data.get("entities", {}).get(entity_id, {})

            # 提取跨平台链接
            sitelinks = entity.get("sitelinks", {})
            external_links = {}
            wiki_map = {
                "zhwiki": "维基百科(中文)",
                "enwiki": "维基百科(英文)",
                "zh_yuewiki": "维基百科(粤语)",
            }
            for key, label in wiki_map.items():
                if key in sitelinks:
                    external_links[label] = sitelinks[key].get("url", "")

            labels = entity.get("labels", {})
            descriptions = entity.get("descriptions", {})

            return {
                "id": entity_id,
                "name": labels.get("zh", {}).get("value", labels.get("en", {}).get("value", "")),
                "description": descriptions.get("zh", {}).get("value", descriptions.get("en", {}).get("value", "")),
                "external_links": external_links,
                "source": "wikidata",
            }
        except Exception as e:
            print(f"Wikidata获取详情错误: {e}")
    return None
