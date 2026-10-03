import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

# Ensure root dir is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ai.datasets.dataset_loader import get_train_test_split, get_default_dataset_path
from ai.datasets.schema import validate_dataset

# Feature definitions
NUMERICAL_FEATURES = [
    "device_age",
    "parts_cost",
    "labor_cost",
    "resale_value",
    "repair_duration",
]

CATEGORICAL_FEATURES = [
    "device_model",
    "issue",
    "condition",
    "repair_outcome",
]

def build_preprocessor() -> ColumnTransformer:
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    return preprocessor

def evaluate_model(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    y_pred = pipeline.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))
    
    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
    }

def train_and_select_best_model(
    dataset_path: str = None,
    output_dir: str = None,
    version: str = "1.0.0"
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Trains candidate ML models (Random Forest, Gradient Boosting), evaluates MAE, RMSE, and R2,
    persists the champion model pipeline and training metadata.
    """
    if output_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_dir, "models")
    os.makedirs(output_dir, exist_ok=True)

    print("--- STEP 20: AI/ML Training Pipeline Initialized ---")
    
    # 1. Load and split validated dataset
    X_train, X_test, y_train, y_test = get_train_test_split(dataset_path)
    print(f"Training set: {len(X_train)} samples | Test set: {len(X_test)} samples")

    preprocessor = build_preprocessor()

    # 2. Candidate Models
    candidates = {
        "RandomForestRegressor": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                n_estimators=120,
                max_depth=12,
                min_samples_split=3,
                random_state=42,
                n_jobs=-1
            ))
        ]),
        "GradientBoostingRegressor": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.08,
                max_depth=5,
                random_state=42
            ))
        ])
    }

    benchmark_results = {}
    best_name = None
    best_pipeline = None
    best_r2 = -float("inf")

    # 3. Train and Benchmark Candidates
    for name, pipeline in candidates.items():
        print(f"\nTraining Candidate: {name}...")
        pipeline.fit(X_train, y_train)
        metrics = evaluate_model(pipeline, X_test, y_test)
        benchmark_results[name] = metrics
        print(f"  Evaluation Metrics -> MAE: ${metrics['mae']:.2f} | RMSE: ${metrics['rmse']:.2f} | R²: {metrics['r2_score']:.4f}")

        if metrics["r2_score"] > best_r2:
            best_r2 = metrics["r2_score"]
            best_name = name
            best_pipeline = pipeline

    print(f"\n[*] Champion Model Selected: {best_name} (R2 = {best_r2:.4f})")

    # 4. Save Versioned Model Artifacts
    model_filename = f"repair_cost_{best_name.lower()}_v{version}.joblib"
    model_filepath = os.path.join(output_dir, model_filename)
    latest_filepath = os.path.join(output_dir, "repair_cost_model_latest.joblib")

    joblib.dump(best_pipeline, model_filepath)
    joblib.dump(best_pipeline, latest_filepath)
    print(f"Model artifact saved to: {model_filepath}")

    # 5. Metadata and Version Registry
    metadata = {
        "model_version": version,
        "champion_model": best_name,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_variable": "repair_cost",
        "evaluation_metrics": benchmark_results[best_name],
        "candidate_benchmarks": benchmark_results,
        "dataset_info": {
            "total_samples": len(X_train) + len(X_test),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "numerical_features": NUMERICAL_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
        },
        "artifact_file": model_filename,
        "is_production_ready": True if best_r2 >= 0.85 else False,
    }

    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Training metadata written to: {metadata_path}")

    return best_pipeline, metadata

if __name__ == "__main__":
    train_and_select_best_model()
