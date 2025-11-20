import streamlit as st
from PIL import Image
from utils import machado, rgb
import json
import os

# ---------------------------
# 設定保存関数（保存だけ）
# ---------------------------
def save_settings(filepath: str, username: str, data: dict):
    all_data = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    all_data[username] = data
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

# ---------------------------
# Streamlit ページ設定
# ---------------------------
st.set_page_config(page_title="色覚特性シミュレーション", layout="centered")
st.title("色覚特性シミュレーションアプリ")

settings_path = "saved_settings.json"

# ---------------------------
# ユーザー管理
# ---------------------------
st.subheader("ユーザー管理")
username = st.text_input("名前を入力してください", "user1")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

# ---------------------------
# 表示名変換
# ---------------------------
def label(name):
    return "正常" if name is None else {
        "Protanomaly":  "P型（赤色盲）",
        "Deuteranomaly":"D型（緑色盲）",
        "Tritanomaly": "T型（青色盲）"
    }[name]

# ---------------------------
# UI 部品
# ---------------------------
color_type = st.selectbox(
    "色覚特性のタイプを選択してください",
    [None, "Protanomaly", "Deuteranomaly", "Tritanomaly"],
    format_func=label,
    index=2
)

severity = st.slider("重症度", 0.0, 1.0, 1.0, 0.05)

st.subheader("細かい調整(数字が大きければ強くなる)")
col_r, col_g, col_b = st.columns(3)
r_gain = col_r.slider("赤色", 0.0, 2.0, 1.0, 0.05)
g_gain = col_g.slider("緑色", 0.0, 2.0, 1.0, 0.05)
b_gain = col_b.slider("青色", 0.0, 2.0, 1.0, 0.05)

# ---------------------------
# 画像処理
# ---------------------------
if uploaded_file:
    src = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.image(src, caption="元の画像", use_column_width=True)

    sim = machado(src, color_type, severity)
    out = rgb(sim, r_gain, g_gain, b_gain)

    with col2:
        st.image(
            out,
            caption=f"{label(color_type)}（重症度 {severity:.2f}） + "
                    f"R×{r_gain:.2f}, G×{g_gain:.2f}, B×{b_gain:.2f}",
            use_column_width=True
        )

# ---------------------------
# 補正値の保存
# ---------------------------
preset_name = st.text_input("補正値の名前", "例：紅葉の補正値")
if st.button("この補正値を保存する"):
    if not username or username.strip() == "":
        st.error("ユーザー名を入力してください")
    else:
        saved_data = {
            "name": preset_name,
            "type": color_type,
            "severity": severity,
            "r_gain": r_gain,
            "g_gain": g_gain,
            "b_gain": b_gain
        }
        save_settings(settings_path, username, saved_data)
        st.success(f"{username} の補正値を保存しました")

