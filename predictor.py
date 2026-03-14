# backend/models/predictor.py
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import numpy as np
import os

class ModelPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        self.load_model(model_path)
    
    def load_model(self, model_path: str = None):
        """
        Carga el modelo entrenado o crea uno por defecto.
        """
        IMG_SIZE = 224
        NUM_CLASSES = 3
        
        # Crear arquitectura base
        base_model = MobileNetV2(
            weights='imagenet', 
            include_top=False, 
            input_shape=(IMG_SIZE, IMG_SIZE, 3)
        )
        base_model.trainable = False
        
        inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.2)(x)
        outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
        
        self.model = models.Model(inputs, outputs)
        
        # Cargar pesos si existen
        if model_path and os.path.exists(model_path):
            self.model.load_weights(model_path)
            print(f"Modelo cargado desde {model_path}")
        else:
            print("Usando modelo base (sin pesos entrenados)")
    
    def predict(self, image_array: np.ndarray) -> np.ndarray:
        """
        Realiza la predicción sobre una imagen preprocesada.
        """
        if self.model is None:
            raise ValueError("El modelo no está cargado")
        
        return self.model.predict(image_array, verbose=0)
    
    def predict_batch(self, images_array: np.ndarray) -> np.ndarray:
        """
        Realiza predicciones por lote.
        """
        if self.model is None:
            raise ValueError("El modelo no está cargado")
        
        return self.model.predict(images_array, verbose=0)