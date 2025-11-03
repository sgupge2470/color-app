from colour.blindness import matrix_cvd_Machado2009
from PIL import Image
import numpy as np
import json
import os

# γ補正: sRGB → Linear RGB（展開）
def srgb_to_linear(arr):
    threshold = 0.04045
    below = arr <= threshold
    above = arr > threshold
    result = np.zeros_like(arr)
    result[below] = arr[below] / 12.92
    result[above] = ((arr[above] + 0.055) / 1.055) ** 2.4
    return result

# γ補正: Linear RGB → sRGB（圧縮）
def linear_to_srgb(arr):
    threshold = 0.0031308
    below = arr <= threshold
    above = arr > threshold
    result = np.zeros_like(arr)
    result[below] = arr[below] * 12.92
    result[above] = 1.055 * (arr[above] ** (1/2.4)) - 0.055
    return result

# Machado法 + γ補正
def machado(image, model_name, severity):
    if model_name is None:
        return image

    arr = np.asarray(image) / 255.0  # [0,1] に正規化
    arr = srgb_to_linear(arr)        # γ展開

    M = matrix_cvd_Machado2009(model_name, severity)
    arr = np.tensordot(arr, M.T, axes=1)

    arr = linear_to_srgb(arr)        # γ圧縮
    arr = (arr * 255).clip(0, 255).astype("uint8")
    return Image.fromarray(arr)

# RGB ゲイン補正
def rgb(image, r_gain=1.0, g_gain=1.0, b_gain=1.0):
    arr = np.asarray(image, dtype=np.float32)
    arr[..., 0] *= r_gain
    arr[..., 1] *= g_gain
    arr[..., 2] *= b_gain
    arr = np.clip(arr, 0, 255).astype("uint8")
    return Image.fromarray(arr)

# 補正値を保存する（ユーザーごとに追加・上書き）
def save_settings(filepath: str, username: str, data: dict):
    all_data = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    all_data[username] = data  # ユーザー名ごとに保存
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
