# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class Probability(BaseModel):
    className: str
    probability: float

class Recommendation(BaseModel):
    title: str
    description: str
    severity: str  # 'low', 'medium', 'high'
    actions: List[str]

class PredictionResult(BaseModel):
    className: str
    confidence: float
    probabilities: List[Probability]
    recommendations: Recommendation

class PredictionResponse(BaseModel):
    success: bool
    prediction: Optional[PredictionResult] = None
    error: Optional[str] = None
    processingTime: float