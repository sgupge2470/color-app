import json
import os

def load_settings(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(filepath, username, data):
    all_data = load_settings(filepath)

    # ユーザー単位にリストで保存
    if username not in all_data:
        all_data[username] = []

    all_data[username].append(data)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def get_user_presets(filepath, username):
    all_data = load_settings(filepath)
    return all_data.get(username, [])
