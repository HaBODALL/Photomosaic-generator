"""
Color space conversions and feature extraction utilities.
"""
import cv2
import numpy as np


def bgr_to_lab(image_bgr: np.ndarray) -> np.ndarray:
    """
    Convert a BGR image (uint8 or float32) to CIELAB float32 representation.
    Returns array in LAB space where L in [0, 100], A/B in [-128, 127].
    """
    if image_bgr.dtype == np.uint8:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    else:
        image_rgb = image_bgr[:, :, ::-1].astype(np.float32)

    image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    return image_lab


def extract_feature_vector(image_bgr: np.ndarray, color_space: str = "lab", sub_grid: int = 2) -> np.ndarray:
    """
    Extract feature vector for a tile or tile region.

    Args:
        image_bgr: Input BGR image array.
        color_space: "lab" for CIELAB, "bgr" or "rgb" for BGR/RGB mean.
        sub_grid: Grid division (1 for 1x1 average, 2 for 2x2 quadrants, etc.)

    Returns:
        1D float32 numpy array representing features.
    """
    if color_space.lower() == "lab":
        img_features = bgr_to_lab(image_bgr)
    else:
        img_features = image_bgr.astype(np.float32)

    h, w, c = img_features.shape

    if sub_grid <= 1:
        return np.mean(img_features, axis=(0, 1)).flatten()

    features = []
    h_step = h / sub_grid
    w_step = w / sub_grid

    for i in range(sub_grid):
        for j in range(sub_grid):
            y_start, y_end = int(i * h_step), int((i + 1) * h_step)
            x_start, x_end = int(j * w_step), int((j + 1) * w_step)
            patch = img_features[y_start:y_end, x_start:x_end, :]
            if patch.size > 0:
                features.append(np.mean(patch, axis=(0, 1)))
            else:
                features.append(np.zeros((c,), dtype=np.float32))

    return np.concatenate(features, axis=0)
