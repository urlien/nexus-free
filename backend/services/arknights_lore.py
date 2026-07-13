"""明日方舟角色设定仓库 - arknights_lore_wiki

数据来源: https://github.com/littlepangding/arknights_lore_wiki
包含1000+角色的详细设定、人物关系、背景故事
"""
import httpx
import re
from typing import List, Optional
from ..models.character import CharacterSearchResult

LORE_API = "https://api.github.com/repos/littlepangding/arknights_lore_wiki/contents/data/char_v3"
LORE_BASE = "https://raw.githubusercontent.com/littlepangding/arknights_lore_wiki/main/data/char_v3/"
ALIAS_URL = "https://raw.githubusercontent.com/littlepangding/arknights_lore_wiki/main/data/char_alias.txt"


async def search_arknights_lore(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索明日方舟角色设定仓库"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # 获取角色别名映射
            alias_map = await _get_alias_map(client)

            # 先用别名匹配
            matched_files = []
            for alias, char_id in alias_map.items():
                if query in alias or alias in query:
                    matched_files.append((alias, f"char_{char_id}.txt"))

            # 如果别名没匹配到，搜索文件名
            if not matched_files:
                resp = await client.get(LORE_API, params={"per_page": 1000})
                if resp.status_code == 200:
                    files = resp.json()
                    for f in files:
                        name = f.get("name", "")
                        if query.lower() in name.lower():
                            matched_files.append((name, name))

            # 获取匹配角色的内容
            for display_name, filename in matched_files[:limit]:
                content = await _get_char_content(client, filename)
                if content:
                    # 提取简要介绍
                    brief = _extract_field(content, "简要介绍")
                    results.append(
                        CharacterSearchResult(
                            name=display_name,
                            source="arknights_lore",
                            url=f"https://github.com/littlepangding/arknights_lore_wiki/blob/main/data/char_v3/{filename}",
                            summary=brief[:200] if brief else f"明日方舟角色设定: {display_name}",
                        )
                    )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="arknights_lore", summary=f"设定搜索出错: {str(e)}"
                )
            )
    return results


async def get_character_lore(filename: str) -> Optional[dict]:
    """获取角色完整设定"""
    async with httpx.AsyncClient(timeout=20) as client:
        content = await _get_char_content(client, filename)
        if content:
            return {
                "name": _extract_field(content, "名称"),
                "aliases": _extract_field(content, "其他名称"),
                "brief": _extract_field(content, "简要介绍"),
                "relations": _extract_field(content, "相关角色"),
                "detail": _extract_field(content, "详细介绍"),
                "source": "arknights_lore",
                "raw": content[:8000],
            }
    return None


async def get_character_relations(filename: str) -> Optional[str]:
    """获取角色人物关系"""
    async with httpx.AsyncClient(timeout=20) as client:
        content = await _get_char_content(client, filename)
        if content:
            return _extract_field(content, "相关角色")
    return None


async def _get_alias_map(client: httpx.AsyncClient) -> dict:
    """获取角色别名映射"""
    try:
        resp = await client.get(ALIAS_URL)
        if resp.status_code == 200:
            alias_map = {}
            for line in resp.text.splitlines():
                if ":" in line:
                    parts = line.split(":", 1)
                    alias = parts[0].strip()
                    char_id = parts[1].strip()
                    alias_map[alias] = char_id
            return alias_map
    except Exception:
        pass
    return {}


async def _get_char_content(client: httpx.AsyncClient, filename: str) -> Optional[str]:
    """获取角色文件内容"""
    try:
        resp = await client.get(f"{LORE_BASE}{filename}")
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None


def _extract_field(content: str, field_name: str) -> str:
    """从角色文件中提取指定字段"""
    pattern = rf"<{field_name}>\s*(.*?)\s*</{field_name}>"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
