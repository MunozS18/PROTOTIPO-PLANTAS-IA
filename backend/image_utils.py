"""Preprocesamiento de imágenes alineado con el entrenamiento."""
from __future__ import annotations

import numpy as np
from PIL import Image

IMG_SIZE = 224


def center_crop_square(img: Image.Image) -> Image.Image:
    """Recorte cuadrado al centro — enfoque en la planta/hoja."""
    img = img.convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def preprocess_pil(img: Image.Image, size: int = IMG_SIZE) -> np.ndarray:
    cropped = center_crop_square(img)
    resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
    arr = np.array(resized, dtype=np.float32) / 255.0
    return arr


def tta_variants(img: Image.Image) -> list[np.ndarray]:
    """Variantes para promedio de predicciones (más robusto en fotos de campo)."""
    base = center_crop_square(img)
    variants: list[Image.Image] = [
        base,
        base.transpose(Image.FLIP_LEFT_RIGHT),
    ]
    # Recorte ligeramente más cerrado (zoom)
    w, h = base.size
    margin = int(min(w, h) * 0.08)
    zoomed = base.crop((margin, margin, w - margin, h - margin))
    variants.append(zoomed)

    return [preprocess_pil(v) for v in variants]
