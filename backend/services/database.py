"""本地数据库服务 - SQLite 卡片库"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional

DB_PATH = os.getenv("NEXUS_DB_PATH", "nexus_free.db")


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT DEFAULT '',
            description TEXT DEFAULT '',
            personality TEXT DEFAULT '',
            scenario TEXT DEFAULT '',
            first_mes TEXT DEFAULT '',
            mes_example TEXT DEFAULT '',
            creator_notes TEXT DEFAULT '',
            system_prompt TEXT DEFAULT '',
            post_history_instructions TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            creator TEXT DEFAULT 'Nexus Free',
            character_version TEXT DEFAULT '2.0',
            image_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS lorebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            entries TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS lorebook_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lorebook_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            keywords TEXT DEFAULT '[]',
            category TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1,
            FOREIGN KEY (lorebook_id) REFERENCES lorebooks(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
        CREATE INDEX IF NOT EXISTS idx_cards_source ON cards(source);
        CREATE INDEX IF NOT EXISTS idx_cards_tags ON cards(tags);
    """)
    conn.commit()
    conn.close()


# === 角色卡 CRUD ===

def create_card(card_data: dict) -> dict:
    """创建角色卡"""
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO cards (name, source, description, personality, scenario, first_mes,
                          mes_example, creator_notes, system_prompt, post_history_instructions,
                          tags, creator, character_version, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        card_data.get("name", ""),
        card_data.get("source", ""),
        card_data.get("description", ""),
        card_data.get("personality", ""),
        card_data.get("scenario", ""),
        card_data.get("first_mes", ""),
        card_data.get("mes_example", ""),
        card_data.get("creator_notes", ""),
        card_data.get("system_prompt", ""),
        card_data.get("post_history_instructions", ""),
        json.dumps(card_data.get("tags", []), ensure_ascii=False),
        card_data.get("creator", "Nexus Free"),
        card_data.get("character_version", "2.0"),
        card_data.get("image_url", ""),
    ))
    card_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_card(card_id)


def get_card(card_id: int) -> Optional[dict]:
    """获取单个角色卡"""
    conn = get_db()
    row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_cards(
    search: str = "",
    source: str = "",
    tag: str = "",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """列出角色卡（支持搜索/筛选/分页）"""
    conn = get_db()
    conditions = []
    params = []

    if search:
        conditions.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if source:
        conditions.append("source = ?")
        params.append(source)
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f"%{tag}%")

    where = " AND ".join(conditions) if conditions else "1=1"
    offset = (page - 1) * per_page

    total = conn.execute(f"SELECT COUNT(*) FROM cards WHERE {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM cards WHERE {where} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        params + [per_page, offset],
    ).fetchall()
    conn.close()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "cards": [dict(r) for r in rows],
    }


def update_card(card_id: int, card_data: dict) -> Optional[dict]:
    """更新角色卡"""
    conn = get_db()
    fields = []
    params = []
    for key in ["name", "source", "description", "personality", "scenario", "first_mes",
                 "mes_example", "creator_notes", "system_prompt", "post_history_instructions",
                 "tags", "creator", "character_version", "image_url"]:
        if key in card_data:
            val = card_data[key]
            if key == "tags" and isinstance(val, list):
                val = json.dumps(val, ensure_ascii=False)
            fields.append(f"{key} = ?")
            params.append(val)

    if not fields:
        conn.close()
        return get_card(card_id)

    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(card_id)

    conn.execute(f"UPDATE cards SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return get_card(card_id)


def delete_card(card_id: int) -> bool:
    """删除角色卡"""
    conn = get_db()
    cursor = conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# === 世界书 CRUD ===

def create_lorebook(name: str, description: str = "") -> dict:
    """创建世界书"""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO lorebooks (name, description) VALUES (?, ?)",
        (name, description),
    )
    lb_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_lorebook(lb_id)


def get_lorebook(lorebook_id: int) -> Optional[dict]:
    """获取世界书（含条目）"""
    conn = get_db()
    row = conn.execute("SELECT * FROM lorebooks WHERE id = ?", (lorebook_id,)).fetchone()
    if not row:
        conn.close()
        return None

    entries = conn.execute(
        "SELECT * FROM lorebook_entries WHERE lorebook_id = ? ORDER BY id",
        (lorebook_id,),
    ).fetchall()
    conn.close()

    result = dict(row)
    result["entries"] = [dict(e) for e in entries]
    return result


def list_lorebooks(page: int = 1, per_page: int = 20) -> dict:
    """列出世界书"""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM lorebooks").fetchone()[0]
    offset = (page - 1) * per_page
    rows = conn.execute(
        "SELECT * FROM lorebooks ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    conn.close()
    return {"total": total, "page": page, "per_page": per_page, "lorebooks": [dict(r) for r in rows]}


def add_lorebook_entry(lorebook_id: int, entry_data: dict) -> dict:
    """添加世界书条目"""
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO lorebook_entries (lorebook_id, title, content, keywords, category)
        VALUES (?, ?, ?, ?, ?)
    """, (
        lorebook_id,
        entry_data.get("title", ""),
        entry_data.get("content", ""),
        json.dumps(entry_data.get("keywords", []), ensure_ascii=False),
        entry_data.get("category", ""),
    ))
    entry_id = cursor.lastrowid
    conn.execute("UPDATE lorebooks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (lorebook_id,))
    conn.commit()
    conn.close()
    row = conn.execute("SELECT * FROM lorebook_entries WHERE id = ?", (entry_id,)).fetchone()
    return dict(row) if row else {}


def delete_lorebook(lorebook_id: int) -> bool:
    """删除世界书"""
    conn = get_db()
    cursor = conn.execute("DELETE FROM lorebooks WHERE id = ?", (lorebook_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# 初始化
init_db()
