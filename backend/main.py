# backend/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import time
from typing import Dict, Any
import uvicorn

from models.predictor import ModelPredictor
from schemas import PredictionResponse, PredictionResult, Recommendation

app = FastAPI(
    title="AgroIdentify Colombia API",
    description="API para identificación de plantas y enfermedades agrícolas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el predictor (se carga una sola vez)
predictor = ModelPredictor()

# Configuración
IMG_SIZE = 224
CLASS_NAMES = ['Tomate Sano', 'Tomate Tizón Tardío', 'Papa Sana']
CONFIDENCE_THRESHOLD = 0.3

@app.get("/")
async def root():
    return {
        "message": "AgroIdentify Colombia API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": predictor.model is not None,
        "classes": CLASS_NAMES
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Endpoint principal para predicción de enfermedades en cultivos.
    Recibe una imagen y devuelve el diagnóstico con recomendaciones.
    """
    start_time = time.time()
    
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="El archivo debe ser una imagen válida"
            )
        
        # Leer y procesar la imagen
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Redimensionar y normalizar
        image = image.resize((IMG_SIZE, IMG_SIZE))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        # Realizar predicción
        predictions = predictor.predict(image_array)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Obtener probabilidades por clase
        probabilities = [
            {"className": CLASS_NAMES[i], "probability": float(predictions[0][i])}
            for i in range(len(CLASS_NAMES))
        ]
        
        # Generar recomendaciones basadas en la predicción
        recommendations = generate_recommendations(
            CLASS_NAMES[predicted_class_idx], 
            confidence
        )
        
        # Crear respuesta
        result = PredictionResult(
            className=CLASS_NAMES[predicted_class_idx],
            confidence=confidence,
            probabilities=probabilities,
            recommendations=recommendations
        )
        
        processing_time = time.time() - start_time
        
        return PredictionResponse(
            success=True,
            prediction=result,
            processingTime=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_recommendations(class_name: str, confidence: float) -> Recommendation:
    """
    Genera recomendaciones personalizadas según el diagnóstico.
    """
    base_recommendations = {
        "Tomate Sano": Recommendation(
            title="Cultivo en Buen Estado",
            description="Tu planta de tomate se encuentra saludable. Continúa con las prácticas de cultivo adecuadas.",
            severity="low",
            actions=[
                "Mantener el riego constante pero sin encharcar",
                "Revisar periódicamente hojas inferiores en busca de signos tempranos",
                "Aplicar fertilizante orgánico cada 15 días",
                "Mantener el área libre de malezas"
            ]
        ),
        "Tomate Tizón Tardío": Recommendation(
            title="Alerta: Tizón Tardío Detectado",
            description="Se ha detectado Phytophthora infestans, un hongo que puede destruir el cultivo rápidamente si no se controla.",
            severity="high",
            actions=[
                "Aplicar fungicidas a base de cobre inmediatamente",
                "Eliminar y destruir las hojas y frutos infectados",
                "Evitar el riego por aspersión para reducir la humedad",
                "Consultar con un técnico agrícola para tratamiento específico",
                "Aislar plantas infectadas si es posible"
            ]
        ),
        "Papa Sana": Recommendation(
            title="Cultivo en Buen Estado",
            description="Tu planta de papa se encuentra saludable. Sigue con las buenas prácticas agrícolas.",
            severity="low",
            actions=[
                "Mantener el suelo húmedo pero bien drenado",
                "Aporcar las plantas para proteger los tubérculos",
                "Vigilar la aparición de plagas como la polilla de la papa",
                "Fertilizar según la etapa de crecimiento"
            ]
        )
    }
    
    return base_recommendations.get(
        class_name,
        Recommendation(
            title="Resultado no concluyente",
            description="No se pudo determinar con certeza el estado del cultivo.",
            severity="medium",
            actions=["Tomar otra foto con mejor iluminación", "Consultar con un técnico agrícola"]
        )
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)