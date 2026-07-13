"""Bangumi 搜索服务 - 中文ACGN数据库"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

BANGUMI_API = "https://api.bgm.tv"


async def search_bangumi(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 Bangumi 角色"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{BANGUMI_API}/search/subject/{query}",
                params={"type": 2, "responseGroup": "small", "max_results": limit},
                headers={"User-Agent": "NexusFree/0.2.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                subjects = data.get("list", [])

                for subject in subjects:
                    results.append(
                        CharacterSearchResult(
                            name=subject.get("name", query),
                            source="bangumi",
                            url=f"https://bgm.tv/subject/{subject.get('id', '')}",
                            image=subject.get("images", {}).get("medium"),
                            summary=subject.get("name_cn", "") or subject.get("summary", "")[:100],
                        )
                    )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="bangumi", summary=f"Bangumi搜索出错: {str(e)}"
                )
            )
    return results


async def search_bangumi_character(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 Bangumi 角色（通过人物搜索接口）"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Bangumi 没有专门的角色搜索 API，用 subject 搜索代替
            resp = await client.get(
                f"{BANGUMI_API}/search/subject/{query}",
                params={"type": 2, "responseGroup": "medium", "max_results": limit},
                headers={"User-Agent": "NexusFree/0.2.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                for subject in data.get("list", []):
                    results.append(
                        CharacterSearchResult(
                            name=subject.get("name", query),
                            source="bangumi",
                            url=f"https://bgm.tv/subject/{subject.get('id', '')}",
                            summary=subject.get("name_cn", ""),
                        )
                    )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="bangumi", summary=f"Bangumi搜索出错: {str(e)}"
                )
            )
    return results


async def get_bangumi_subject(subject_id: int) -> Optional[dict]:
    """获取 Bangumi 条目详情"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{BANGUMI_API}/subject/{subject_id}",
                headers={"User-Agent": "NexusFree/0.2.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "name": data.get("name", ""),
                    "name_cn": data.get("name_cn", ""),
                    "summary": data.get("summary", ""),
                    "image": data.get("images", {}).get("medium"),
                    "url": f"https://bgm.tv/subject/{subject_id}",
                    "source": "bangumi",
                }
        except Exception as e:
            print(f"Bangumi获取详情错误: {e}")
    return None
