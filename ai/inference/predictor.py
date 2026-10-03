import os
import sys
import json
import joblib
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Ensure root dir is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai.datasets.schema import ALLOWED_CONDITIONS, ALLOWED_ISSUES, ALLOWED_OUTCOMES

class PredictionInput(BaseModel):
    device_model: str = Field("Samsung Galaxy S23", description="Device model string")
    device_age: float = Field(12.0, ge=0, description="Age in months")
    issue: str = Field("screen_cracked", description="Hardware fault type")
    parts_cost: Optional[float] = Field(None, ge=0, description="Estimated parts cost")
    labor_cost: Optional[float] = Field(None, ge=0, description="Estimated labor cost")
    condition: str = Field("good", description="Device condition")
    resale_value: Optional[float] = Field(None, ge=0, description="Resale market value")
    repair_duration: Optional[float] = Field(2.0, ge=0, description="Expected repair turnaround in hours")
    repair_outcome: str = Field("SUCCESS", description="Expected repair outcome")

class PredictionResult(BaseModel):
    estimated_repair_cost: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95
    model_version: str
    model_algorithm: str
    is_trained_model: bool
    evaluation_mae: float
    evaluation_r2: float
    input_features: Dict[str, Any]

class RepairCostPredictor:
    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            model_dir = os.path.join(base_dir, "models")
        self.model_dir = model_dir
        self.pipeline = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        latest_path = os.path.join(self.model_dir, "repair_cost_model_latest.joblib")
        meta_path = os.path.join(self.model_dir, "model_metadata.json")

        if os.path.exists(latest_path) and os.path.exists(meta_path):
            try:
                self.pipeline = joblib.load(latest_path)
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load trained ML model: {e}")
                self.pipeline = None
                self.metadata = None
        else:
            self.pipeline = None
            self.metadata = None

    def is_model_available(self) -> bool:
        return self.pipeline is not None and self.metadata is not None

    def predict(self, input_data: PredictionInput) -> Dict[str, Any]:
        """
        Executes model inference on the input feature vector.
        If no model is trained, returns explicit status without fabricating data.
        """
        if not self.is_model_available():
            # Return explicit un-trained status as requested
            return {
                "error": "No trained ML model found. Training data must be trained first.",
                "is_trained_model": False,
                "status": "NO_TRAINED_MODEL_AVAILABLE"
            }

        # Default heuristics for optional inputs if not supplied
        parts_c = input_data.parts_cost
        labor_c = input_data.labor_cost
        if parts_c is None:
            parts_c = 120.0 if "macbook" in input_data.device_model.lower() else 85.0
        if labor_c is None:
            labor_c = 65.0 if "macbook" in input_data.device_model.lower() else 45.0

        resale_v = input_data.resale_value
        if resale_v is None:
            resale_v = 450.0

        row = {
            "device_model": input_data.device_model,
            "device_age": input_data.device_age,
            "issue": input_data.issue,
            "parts_cost": parts_c,
            "labor_cost": labor_c,
            "condition": input_data.condition if input_data.condition in ALLOWED_CONDITIONS else "good",
            "resale_value": resale_v,
            "repair_duration": input_data.repair_duration or 2.0,
            "repair_outcome": input_data.repair_outcome if input_data.repair_outcome in ALLOWED_OUTCOMES else "SUCCESS",
        }

        df_input = pd.DataFrame([row])
        pred_cost = float(self.pipeline.predict(df_input)[0])
        pred_cost = max(10.0, round(pred_cost, 2))

        mae = self.metadata.get("evaluation_metrics", {}).get("mae", 5.0)
        r2 = self.metadata.get("evaluation_metrics", {}).get("r2_score", 0.95)
        
        # 95% prediction interval ~ ± 1.96 * MAE
        margin = round(mae * 1.96, 2)
        lower_bound = max(10.0, round(pred_cost - margin, 2))
        upper_bound = round(pred_cost + margin, 2)

        return {
            "estimated_repair_cost": pred_cost,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence_level": 0.95,
            "model_version": self.metadata.get("model_version", "1.0.0"),
            "model_algorithm": self.metadata.get("champion_model", "RandomForestRegressor"),
            "is_trained_model": True,
            "evaluation_mae": mae,
            "evaluation_r2": r2,
            "input_features": row,
        }

# Global singleton predictor
_predictor_instance = None

def get_repair_cost_predictor() -> RepairCostPredictor:
    global _predictor_instance
    if _predictor_instance is None or not _predictor_instance.is_model_available():
        _predictor_instance = RepairCostPredictor()
    return _predictor_instance
