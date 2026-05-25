import io
import json
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from models.predictor import ModelPredictor
from prediction_utils import analyze_predictions
from recommendations import generate_recommendations
from schemas import AnalysisSummary, PredictionResponse, PredictionResult, Probability

app = FastAPI(
    title="AgroPlantas Colombia API",
    description="Identificación de plantas agrícolas y malezas con IA",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from supported_species import get_supported_species

predictor = ModelPredictor()
CONFIDENCE_THRESHOLD = 0.50


@app.get("/")
async def root():
    return {
        "message": "AgroPlantas Colombia — API de identificación vegetal",
        "version": "2.1.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    metrics_path = Path(__file__).resolve().parents[1] / "models" / "training_metrics.json"
    metrics = {}
    if metrics_path.exists():
        with open(metrics_path, encoding="utf-8") as f:
            metrics = json.load(f)

    return {
        "status": "healthy",
        "model_loaded": predictor.model is not None,
        "model_trained": predictor.is_ready(),
        "classes": predictor.get_class_names(),
        "num_classes": len(predictor.get_class_names()),
        "training_metrics": metrics or None,
    }



@app.get("/api/classes")
async def list_classes():
    return {"classes": predictor.get_class_names()}


@app.get("/api/supported-species")
async def supported_species():
    return {"species": get_supported_species(), "count": len(get_supported_species())}


@app.post("/api/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen válida")

        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx. 10 MB)")

        image = Image.open(io.BytesIO(contents))

        if not predictor.is_ready():
            raise HTTPException(
                status_code=503,
                detail="Modelo no entrenado. Ejecuta prepare_dataset.py y train.py",
            )

        predictions = predictor.predict_image(image)
        class_names = predictor.get_class_names()

        if len(predictions) != len(class_names):
            raise HTTPException(status_code=500, detail="Desajuste entre modelo y clases")

        analysis_raw = analyze_predictions(class_names, predictions)
        final_class = analysis_raw["finalClass"]
        confidence = analysis_raw["confidence"]

        probabilities = [
            Probability(className=class_names[i], probability=float(predictions[i]))
            for i in range(len(class_names))
        ]
        probabilities.sort(key=lambda p: p.probability, reverse=True)

        plant_info = generate_recommendations(final_class, confidence, analysis_raw)

        analysis = AnalysisSummary(
            recognized=analysis_raw.get("recognized", True),
            speciesName=analysis_raw["speciesName"],
            speciesConfidence=analysis_raw["speciesConfidence"],
            statusLabel=analysis_raw["statusLabel"],
            conditionShort=analysis_raw["conditionShort"],
            isHealthy=analysis_raw["isHealthy"],
            hasPest=analysis_raw["hasPest"],
            hasDisease=analysis_raw["hasDisease"],
            uncertain=analysis_raw["uncertain"],
            alternativeSpecies=analysis_raw["alternativeSpecies"],
            supportedSpecies=analysis_raw.get("supportedSpecies", []),
            rejectionReason=analysis_raw.get("rejectionReason"),
            weakGuessSpecies=analysis_raw.get("weakGuessSpecies"),
            weakGuessConfidence=analysis_raw.get("weakGuessConfidence"),
        )

        low_conf = not analysis_raw.get("recognized", True) or (
            confidence < CONFIDENCE_THRESHOLD or analysis_raw["uncertain"]
        )

        result = PredictionResult(
            className=final_class,
            confidence=confidence,
            probabilities=probabilities,
            analysis=analysis,
            plantInfo=plant_info,
            recommendations=plant_info,
            lowConfidence=low_conf,
        )

        return PredictionResponse(
            success=True,
            prediction=result,
            processingTime=time.time() - start_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
