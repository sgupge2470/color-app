import streamlit as st
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def save_preset(username, data):
    supabase.table("presets").insert({
        "username": username,
        "preset_name": data["名前"],
        "color_type": data["型"],
        "severity": data["シミュレーション強度"],
        "r_gain": data["赤"],
        "g_gain": data["緑"],
        "b_gain": data["青"],
    }).execute()

def load_all_presets_grouped():
    res = supabase.table("presets").select("*").execute()
    data = res.data

    grouped = {}

    for row in data:
        username = row["username"]

        preset = {
            "名前": row["preset_name"],
            "型": row["color_type"],
            "重症度": row["severity"],
            "赤": row["r_gain"],
            "緑": row["g_gain"],
            "青": row["b_gain"],
            "作成日時": row["created_at"]
        }

        if username not in grouped:
            grouped[username] = []

        grouped[username].append(preset)

    return grouped

