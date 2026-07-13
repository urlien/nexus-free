"""明日方舟剧情数据源 - ArknightsStoryTextReader

数据来源:
- 剧情索引: https://r2.m31ns.top/zh_CN/gamedata/excel/story_review_table.json
- 剧情原文: https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/story/[storyTxt].txt
- PRTS Wiki: https://prts.wiki/api.php
"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

STORY_INDEX_URL = "https://r2.m31ns.top/zh_CN/gamedata/excel/story_review_table.json"
STORY_BASE_URL = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/story/"


async def search_arknights_story(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索明日方舟剧情（按活动名/章节名）"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(STORY_INDEX_URL)
            if resp.status_code == 200:
                data = resp.json()
                # 搜索匹配的剧情
                for story_id, story_info in data.items():
                    name = story_info.get("name", "")
                    if query.lower() in name.lower() or query in name:
                        story_txt = story_info.get("storyTxt", "")
                        results.append(
                            CharacterSearchResult(
                                name=name,
                                source="arknights_story",
                                url=f"{STORY_BASE_URL}{story_txt}",
                                summary=f"剧情: {name} (ID: {story_id})",
                            )
                        )
                        if len(results) >= limit:
                            break
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="arknights_story", summary=f"剧情搜索出错: {str(e)}"
                )
            )
    return results


async def get_story_text(story_txt: str) -> Optional[str]:
    """获取剧情原文"""
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(f"{STORY_BASE_URL}{story_txt}")
            if resp.status_code == 200:
                return resp.text[:15000]  # 限制长度
        except Exception as e:
            print(f"剧情获取错误: {e}")
    return None


async def search_character_stories(character_name: str) -> List[dict]:
    """搜索角色相关的所有剧情"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(STORY_INDEX_URL)
            if resp.status_code == 200:
                data = resp.json()
                for story_id, story_info in data.items():
                    name = story_info.get("name", "")
                    # 搜索包含角色名的剧情
                    if character_name in name:
                        results.append({
                            "id": story_id,
                            "name": name,
                            "storyTxt": story_info.get("storyTxt", ""),
                            "type": story_info.get("type", ""),
                        })
        except Exception as e:
            print(f"角色剧情搜索错误: {e}")
    return results[:20]


async def get_story_relationships(story_text: str) -> list:
    """从剧情文本中提取角色关系"""
    # 简单的基于对话提取
    import re
    # 提取对话中的角色名
    speakers = re.findall(r'【([^】]+)】', story_text)
    speakers = list(set(speakers))
    return speakers
