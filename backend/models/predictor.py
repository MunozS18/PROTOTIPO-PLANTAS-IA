import json
import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

from image_utils import tta_variants

IMG_SIZE = 224
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


class ModelPredictor:
    def __init__(self, model_path: str | None = None):
        self.model: tf.keras.Model | None = None
        self.class_names: list[str] = []
        self.model_loaded = False
        self.load_model(model_path)

    def load_model(self, model_path: str | None = None):
        keras_path = MODELS_DIR / "plant_classifier.keras"
        weights_path = MODELS_DIR / "best_weights.keras"
        class_names_path = MODELS_DIR / "class_names.json"

        if class_names_path.exists():
            with open(class_names_path, encoding="utf-8") as f:
                self.class_names = json.load(f)
        else:
            self.class_names = []

        if keras_path.exists():
            self.model = tf.keras.models.load_model(str(keras_path))
            self.model_loaded = True
            print(f"Modelo cargado: {keras_path} ({len(self.class_names)} clases)")
            return

        if model_path and os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            self.model_loaded = True
            return

        if not self.class_names:
            raise RuntimeError(
                "No hay modelo entrenado. Ejecuta prepare_dataset.py y train.py"
            )

        num_classes = len(self.class_names)
        base_model = MobileNetV2(
            weights="imagenet",
            include_top=False,
            input_shape=(IMG_SIZE, IMG_SIZE, 3),
        )
        base_model.trainable = False

        inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(num_classes, activation="softmax")(x)
        self.model = models.Model(inputs, outputs)

        if weights_path.exists() and num_classes >= 2:
            self.model.load_weights(str(weights_path))
            self.model_loaded = True

    def predict(self, image_array: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise ValueError("El modelo no está cargado")
        return self.model.predict(image_array, verbose=0)

    def predict_image(self, pil_image: Image.Image) -> np.ndarray:
        """Predicción con TTA (promedio de varias vistas de la imagen)."""
        variants = tta_variants(pil_image)
        batch = np.stack(variants, axis=0)
        preds = self.predict(batch)
        return np.mean(preds, axis=0)

    def get_class_names(self) -> list[str]:
        return self.class_names

    def is_ready(self) -> bool:
        return self.model_loaded and len(self.class_names) >= 2
