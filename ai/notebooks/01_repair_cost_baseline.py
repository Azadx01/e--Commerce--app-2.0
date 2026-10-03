# # STEP 20 — AI/ML Foundation: Repair Cost Baseline Model
# 
# This document outlines the empirical dataset schema, preprocessing pipeline,
# candidate model benchmarking (Random Forest vs Gradient Boosting), and evaluation metrics.

import os
import pandas as pd
import numpy as np
from ai.datasets.dataset_loader import load_repair_dataset, get_train_test_split
from ai.training.train import train_and_select_best_model
from ai.inference.predictor import get_repair_cost_predictor, PredictionInput

def run_exploratory_analysis():
    print("================================================================")
    print(" ReVivo AI/ML Foundation — Exploratory Data Analysis & Baseline")
    print("================================================================")

    # 1. Dataset Inspection
    df, report = load_repair_dataset()
    print(f"\n[1] Dataset Summary:")
    print(f"    Total Records: {report['rows']}")
    print(f"    Unique Device Models: {report['models_count']}")
    print(f"    Missing / Null values: {report['total_nulls']}")
    print(f"\n    Sample Records:\n", df.head(3).to_string())

    # 2. Target Variable Distribution
    target = df["repair_cost"]
    print(f"\n[2] Target Variable ('repair_cost') Statistics:")
    print(f"    Mean: ${target.mean():.2f}")
    print(f"    Std Dev: ${target.std():.2f}")
    print(f"    Median: ${target.median():.2f}")
    print(f"    Min: ${target.min():.2f} | Max: ${target.max():.2f}")

    # 3. Model Training & Evaluation
    print(f"\n[3] Candidate Model Training & Benchmarking:")
    champion_pipeline, metadata = train_and_select_best_model()

    print(f"\n[4] Benchmark Results Summary:")
    for model_name, metrics in metadata["candidate_benchmarks"].items():
        print(f"    - {model_name}:")
        print(f"        MAE:  ${metrics['mae']:.2f}")
        print(f"        RMSE: ${metrics['rmse']:.2f}")
        print(f"        R²:   {metrics['r2_score']:.4f}")

    print(f"\n[5] Live Sample Inference Test:")
    predictor = get_repair_cost_predictor()
    sample_input = PredictionInput(
        device_model="Samsung Galaxy S23",
        device_age=8.0,
        issue="screen_cracked",
        parts_cost=145.0,
        labor_cost=65.0,
        condition="good"
    )
    result = predictor.predict(sample_input)
    print(f"    Device: {sample_input.device_model} (Issue: {sample_input.issue})")
    print(f"    Predicted Repair Cost: ${result['estimated_repair_cost']:.2f}")
    print(f"    95% Confidence Interval: [${result['lower_bound']:.2f} — ${result['upper_bound']:.2f}]")
    print(f"    Model Version: {result['model_version']} ({result['model_algorithm']})")
    print("================================================================")

if __name__ == "__main__":
    run_exploratory_analysis()
