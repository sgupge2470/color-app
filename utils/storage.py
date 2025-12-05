import sqlite3
import json
from datetime import datetime

DB_PATH = "settings.db"

# -------------------------------
# DB初期化
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
# 保存（上書き対応）
# -------------------------------
def save_settings(username, data):
    preset_name = data.get("名前")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

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
# ユーザー別取得
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


# -------------------------------
# 管理者用：全データ取得
# -------------------------------
def load_settings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT username, data FROM presets
        ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()

    result = {}
    for username, data_json in rows:
        result.setdefault(username, []).append(json.loads(data_json))

    return result
