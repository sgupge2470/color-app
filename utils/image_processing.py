from colour.blindness import matrix_cvd_Machado2009
from PIL import Image
import numpy as np

# ===== γ補正（高速ベクトル化） =====
def srgb_to_linear(arr):
    arr = arr.astype(np.float32)
    arr /= 255.0
    return np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)

def linear_to_srgb(arr):
    arr = np.where(arr <= 0.0031308, arr * 12.92, 1.055 * np.power(arr, 1 / 2.4) - 0.055)
    arr = np.clip(arr, 0.0, 1.0)
    return (arr * 255).astype(np.uint8)

# ===== Machado法 =====
def machado(image, model_name, severity):
    if model_name is None:
        return image

    arr = np.asarray(image, dtype=np.float32)
    arr_lin = srgb_to_linear(arr)  # Linear RGB

    M = matrix_cvd_Machado2009(model_name, severity)
    arr_lin = np.tensordot(arr_lin, M.T, axes=1)

    arr_srgb = linear_to_srgb(arr_lin)
    return Image.fromarray(arr_srgb)

# ===== RGB補正（常にLinear RGB空間） =====
def rgb_gain(image, r_gain=1.0, g_gain=1.0, b_gain=1.0):
    arr = np.asarray(image, dtype=np.float32)
    arr_lin = srgb_to_linear(arr)

    arr_lin[..., 0] *= r_gain
    arr_lin[..., 1] *= g_gain
    arr_lin[..., 2] *= b_gain

    arr_srgb = linear_to_srgb(arr_lin)
    return Image.fromarray(arr_srgb)
