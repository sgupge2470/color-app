import json
import os

def load_settings(settings_path="saved_settings.json"):
    """全ユーザーの補正値を読み込む"""
    if not os.path.exists(settings_path):
        return {}
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings_path, username, data):
    """ユーザー補正値を追記して保存（日本語キー対応）"""
    settings = load_settings(settings_path)
    
    if username not in settings:
        settings[username] = []
    
    # 同名プリセットがあれば上書き（"名前" で比較）
    for i, preset in enumerate(settings[username]):
        if preset.get("名前") == data.get("名前"):
            settings[username][i] = data
            break
    else:
        settings[username].append(data)

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_user_presets(settings_path, username):
    """特定ユーザーの補正値一覧を取得"""
    settings = load_settings(settings_path)
    return settings.get(username, [])

