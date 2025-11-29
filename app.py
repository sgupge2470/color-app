import streamlit as st
from PIL import Image
from utils.image_processing import machado, rgb_gain
from utils.storage import save_settings, get_user_presets, load_settings
import os
import json

st.set_page_config(page_title="色覚特性シミュレーション", layout="centered")
st.title("色覚特性シミュレーションアプリ")

settings_path = "saved_settings.json"
MAX_WIDTH = 800

# ===== ユーザー管理 =====
st.subheader("ユーザー管理")
username = st.text_input("名前を入力してください", "user1")
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

# ===== 色覚タイプ選択 =====
def label(name):
    return "正常" if name is None else {
        "赤色盲": "P型（赤色盲）",
        "緑色盲":"D型（緑色盲）",
        "青色盲":  "T型（青色盲）"
    }[name]

color_type = st.selectbox(
    "色覚特性のタイプを選択してください",
    [None, "赤色盲", "緑色盲", "青色盲"],
    format_func=label,
    index=2
)

severity = st.slider("重症度", 0.0, 1.0, 1.0, 0.05)

# ===== RGB補正 =====
st.subheader("細かい調整（Linear RGB 空間で補正）")
col_r, col_g, col_b = st.columns(3)
r_gain = col_r.slider("赤色", 0.0, 2.0, 1.0, 0.05)
g_gain = col_g.slider("緑色", 0.0, 2.0, 1.0, 0.05)
b_gain = col_b.slider("青色", 0.0, 2.0, 1.0, 0.05)

# ===== 画像処理 =====
if uploaded_file:
    src = Image.open(uploaded_file).convert("RGB")
    proc_img = src.copy()
    if max(proc_img.size) > MAX_WIDTH:
        proc_img.thumbnail((MAX_WIDTH, MAX_WIDTH))

    col1, col2 = st.columns(2)
    with col1:
        st.image(proc_img, caption="元の画像", use_column_width=True)

    sim = machado(proc_img, color_type, severity)
    out = rgb_gain(sim, r_gain, g_gain, b_gain)

    display_img = out.copy()
    display_img.thumbnail((MAX_WIDTH, MAX_WIDTH))
    with col2:
        st.image(display_img, caption=f"{label(color_type)} + RGB補正", use_column_width=True)

# ===== 保存 & ダウンロード =====
preset_name = st.text_input("補正値の名前", "〇〇の補正値")
if st.button("この補正値を保存する"):
    if not username.strip():
        st.error("ユーザー名を入力してください")
    else:
        data = {
            "名前": preset_name,
            "型": color_type,
            "重症度": severity,
            "赤": r_gain,
            "緑": g_gain,
            "青": b_gain,
        }
        save_settings(settings_path, username, data)
        st.success(f"{username} の新しいプリセットを保存しました！")

        # ダウンロード用JSON
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            label="この補正値をJSONでダウンロード",
            data=json_str,
            file_name=f"{username}_{preset_name}.json",
            mime="application/json"
        )

# ===== 管理者用全ユーザー確認 =====
st.subheader("全ユーザー補正値の確認")
all_settings = load_settings(settings_path)
st.json(all_settings)

