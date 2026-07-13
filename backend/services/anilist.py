"""AniList 搜索服务 - 动漫角色数据库"""
import httpx
from typing import List, Optional
from ..models.character import CharacterSearchResult

ANILIST_API = "https://graphql.anilist.co"

CHARACTER_SEARCH_QUERY = """
query ($search: String, $perPage: Int) {
  Character(search: $search, perPage: $perPage) {
    id
    name { full native alternative }
    image { large medium }
    description
    age
    gender
    dateOfBirth { year month day }
    bloodType
    siteUrl
    media(perPage: 5, type: ANIME) {
      nodes {
        title { romaji english }
        type
      }
    }
  }
}
"""

CHARACTER_SEARCH_LIST_QUERY = """
query ($search: String, $perPage: Int) {
  Page(perPage: $perPage) {
    characters(search: $search) {
      id
      name { full native }
      image { medium }
      siteUrl
      media(perPage: 3, type: ANIME) {
        nodes { title { romaji english } }
      }
    }
  }
}
"""


async def search_anilist(query: str, limit: int = 5) -> List[CharacterSearchResult]:
    """搜索 AniList 角色"""
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                ANILIST_API,
                json={
                    "query": CHARACTER_SEARCH_LIST_QUERY,
                    "variables": {"search": query, "perPage": limit},
                },
            )
            data = resp.json()
            characters = data.get("data", {}).get("Page", {}).get("characters", [])

            for char in characters:
                name = char.get("name", {})
                full_name = name.get("full", "")
                media_list = char.get("media", {}).get("nodes", [])
                works = [m.get("title", {}).get("romaji", "") for m in media_list]
                works = [w for w in works if w]

                results.append(
                    CharacterSearchResult(
                        name=full_name,
                        source="anilist",
                        url=char.get("siteUrl", ""),
                        image=char.get("image", {}).get("medium"),
                        summary=f"{'、'.join(works[:3])}" if works else "AniList角色",
                    )
                )
        except Exception as e:
            results.append(
                CharacterSearchResult(
                    name=query, source="anilist", summary=f"AniList搜索出错: {str(e)}"
                )
            )
    return results


async def get_anilist_character(character_id: int) -> Optional[dict]:
    """获取 AniList 角色详情"""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                ANILIST_API,
                json={
                    "query": CHARACTER_SEARCH_QUERY,
                    "variables": {"search": str(character_id)},
                },
            )
            data = resp.json()
            char = data.get("data", {}).get("Character")
            if char:
                return {
                    "name": char["name"]["full"],
                    "native": char["name"].get("native"),
                    "aliases": char["name"].get("alternative", []),
                    "description": char.get("description", ""),
                    "age": char.get("age"),
                    "gender": char.get("gender"),
                    "image": char.get("image", {}).get("large"),
                    "url": char.get("siteUrl", ""),
                    "source": "anilist",
                }
        except Exception as e:
            print(f"AniList获取详情错误: {e}")
    return None
