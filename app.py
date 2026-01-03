import streamlit as st
from PIL import Image
from utils.image_processing import machado, rgb_gain
from utils.supabase_storage import save_preset, load_all_presets_grouped
import json

# ============================
# セッション初期化（最重要）
# ============================
if "prev_image_name" not in st.session_state:
    st.session_state.prev_image_name = None

if "r_gain" not in st.session_state:
    st.session_state.r_gain = 1.0

if "g_gain" not in st.session_state:
    st.session_state.g_gain = 1.0

if "b_gain" not in st.session_state:
    st.session_state.b_gain = 1.0

if "severity" not in st.session_state:
    st.session_state.severity = 1.0

# ============================
# アプリ基本設定
# ============================
st.set_page_config(page_title="色覚特性シミュレーション", layout="centered")
st.title("色覚特性シミュレーションアプリ")

MAX_WIDTH = 800

# ============================
# ユーザー管理
# ============================
st.subheader("ユーザー登録")
username = st.text_input("名前（ニックネーム）を入力してください", "")
uploaded_file = st.file_uploader("Browse files をクリックし画像を選択してください", type=["jpg", "jpeg", "png"])

# ============================
# 画像が変わったら補正値をリセット
# ============================
if uploaded_file is not None:
    if st.session_state.prev_image_name != uploaded_file.name:
        st.session_state.prev_image_name = uploaded_file.name
        st.session_state.r_gain = 1.0
        st.session_state.g_gain = 1.0
        st.session_state.b_gain = 1.0
        st.session_state.severity = 1.0

# ============================
# 色覚タイプ選択
# ============================
def label(name):
    return "特性なし" if name is None else {
        "赤色覚特性": "P型（赤色覚特性）",
        "緑色覚特性": "D型（緑色覚特性）",
        "青色覚特性": "T型（青色覚特性）"
    }[name]

color_type = st.selectbox(
    "色覚特性のタイプ（選択すると画像が変化するので見え方に近いものを選択してください）",
    [None, "赤色覚特性", "緑色覚特性", "青色覚特性"],
    format_func=label,
    index=2
)

# ============================
# RGB補正
# ============================
st.subheader("細かい調整（数字が大きいほど色が強くなる）")
col_r, col_g, col_b = st.columns(3)

r_gain = col_r.slider("赤色", 0.0, 2.0, st.session_state.r_gain, 0.05, key="r_gain")
g_gain = col_g.slider("緑色", 0.0, 2.0, st.session_state.g_gain, 0.05, key="g_gain")
b_gain = col_b.slider("青色", 0.0, 2.0, st.session_state.b_gain, 0.05, key="b_gain")

# ============================
# 重症度
# ============================
st.subheader("シミュレーション強度（上記以外の補正）")
severity = st.slider("シミュレーション強度", 0.0, 1.0, st.session_state.severity, 0.05, key="severity")

# ============================
# 画像処理
# ============================

if uploaded_file:
    src = Image.open(uploaded_file).convert("RGB")
    proc_img = src.copy()
    if max(proc_img.size) > MAX_WIDTH:
        proc_img.thumbnail((MAX_WIDTH, MAX_WIDTH))

    cvd_map = {
        None: None,
        "赤色覚特性": "protanomaly",
        "緑色覚特性": "deuteranomaly",
        "青色覚特性": "tritanomaly"
    }

    cvd_type = cvd_map[color_type]

    col1, col2 = st.columns(2)
    with col1:
        st.image(proc_img, caption="元の画像", use_column_width=True)

    sim = machado(proc_img, cvd_type, severity)
    out = rgb_gain(sim, r_gain, g_gain, b_gain)

    display_img = out.copy()
    display_img.thumbnail((MAX_WIDTH, MAX_WIDTH))
    with col2:
        st.image(display_img, caption=f"{label(color_type)} + RGB補正", use_column_width=True)

# ============================
# 保存 & ダウンロード（Supabase対応）
# ============================
preset_name = st.text_input("補正値の名前", "例：紅葉の補正値")

if st.button("この補正値を保存する"):
    if not username.strip():
        st.error("ユーザー名を入力してください")
    else:
        data = {
            "名前": preset_name,
            "型": color_type,
            "シミュレーション強度": severity,
            "赤": r_gain,
            "緑": g_gain,
            "青": b_gain,
        }

        # ✅ Supabase に保存
        save_preset(username, data)

        st.success(f"{username} さんの補正値をに保存しました！")

        #✅ JSON ダウンロード（個人バックアップ用）
        #json_str = json.dumps(data, ensure_ascii=False, indent=2)
        #st.download_button(
         #   label="この補正値をJSONでダウンロード（バックアップ用）",
          #  data=json_str,
           # file_name=f"{username}_{preset_name}.json",
            #mime="application/json"
        #)


# ============================
# 管理者用：全ユーザー補正値の確認（Supabase）
# ============================

#from utils.supabase_storage import save_preset, load_all_presets_grouped

#st.subheader("全ユーザー補正値の確認（ユーザーごと）")
#all_settings = load_all_presets_grouped()
#st.json(all_settings)














