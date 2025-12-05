import sqlite3
import json
from datetime import datetime

DB_PATH = "settings.db"

# -------------------------------
# DB初期化（最初に1回だけ実行されればOK）
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            preset_name TEXT,
            data TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# -------------------------------
# 保存（JSON方式の上位互換）
# -------------------------------
def save_settings(username, data):
    """
    data は今まで通りの辞書：
    {
        "名前": "...",
        "R": 0.1,
        "G": 0.2,
        ...
    }
    """
    preset_name = data.get("名前")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 同名プリセットがあれば上書き
    c.execute("""
        SELECT id FROM presets
        WHERE username = ? AND preset_name = ?
    """, (username, preset_name))

    row = c.fetchone()

    if row:
        c.execute("""
            UPDATE presets
            SET data = ?, created_at = ?
            WHERE id = ?
        """, (
            json.dumps(data, ensure_ascii=False),
            datetime.now().isoformat(),
            row[0]
        ))
    else:
        c.execute("""
            INSERT INTO presets (username, preset_name, data, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            preset_name,
            json.dumps(data, ensure_ascii=False),
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()


# -------------------------------
# 読み込み（今までと同じ使い方）
# -------------------------------
def get_user_presets(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT data FROM presets
        WHERE username = ?
        ORDER BY created_at DESC
    """, (username,))

    rows = c.fetchall()
    conn.close()

    return [json.loads(row[0]) for row in rows]
