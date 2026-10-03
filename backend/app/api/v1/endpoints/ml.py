import os
import sys
import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# Ensure root workspace is on sys.path for ai module
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from ai.inference.predictor import (
    get_repair_cost_predictor,
    PredictionInput,
    PredictionResult
)
from ai.training.train import train_and_select_best_model
from app.api import deps
from app.models.user import User

router = APIRouter()

class ModelInfoResponse(BaseModel):
    is_model_available: bool
    model_version: Optional[str] = None
    champion_model: Optional[str] = None
    trained_at_utc: Optional[str] = None
    evaluation_metrics: Optional[Dict[str, float]] = None
    dataset_info: Optional[Dict[str, Any]] = None
    candidate_benchmarks: Optional[Dict[str, Any]] = None

@router.post("/predict-repair-cost", response_model=Dict[str, Any])
def predict_repair_cost(
    input_data: PredictionInput,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Predicts estimated hardware repair cost based on device model, age, issue, and diagnostics.
    Returns point estimate, 95% confidence bounds, and model evaluation metrics.
    """
    predictor = get_repair_cost_predictor()
    result = predictor.predict(input_data)
    
    if not result.get("is_trained_model", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result.get("error", "No trained model currently available.")
        )
    return result

@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_metadata(
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Returns the active AI model version, training metrics (MAE, RMSE, R2), and benchmark comparison.
    """
    predictor = get_repair_cost_predictor()
    if not predictor.is_model_available():
        return {
            "is_model_available": False,
            "model_version": None,
            "champion_model": None,
            "trained_at_utc": None,
            "evaluation_metrics": None,
            "dataset_info": None,
            "candidate_benchmarks": None
        }

    meta = predictor.metadata or {}
    return {
        "is_model_available": True,
        "model_version": meta.get("model_version", "1.0.0"),
        "champion_model": meta.get("champion_model", "RandomForestRegressor"),
        "trained_at_utc": meta.get("trained_at_utc"),
        "evaluation_metrics": meta.get("evaluation_metrics"),
        "dataset_info": meta.get("dataset_info"),
        "candidate_benchmarks": meta.get("candidate_benchmarks"),
    }

@router.post("/train", response_model=Dict[str, Any])
def train_model_endpoint(
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Admin-only endpoint to trigger ML model training pipeline and update active model version.
    """
    pipeline, metadata = train_and_select_best_model()
    # Invalidate predictor singleton cache
    get_repair_cost_predictor()._load_model()
    return {
        "message": "Model training completed successfully.",
        "champion_model": metadata.get("champion_model"),
        "model_version": metadata.get("model_version"),
        "metrics": metadata.get("evaluation_metrics"),
    }
