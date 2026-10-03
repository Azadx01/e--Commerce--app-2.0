import os
import sys
from typing import Tuple, Dict, Any, Optional
import pandas as pd
from sklearn.model_selection import train_test_split

# Ensure root dir is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai.datasets.schema import validate_dataset, REQUIRED_COLUMNS

def get_default_dataset_path() -> str:
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "repair_cost_training.csv")
    if not os.path.exists(csv_path):
        from ai.datasets.generate_seed_dataset import save_default_dataset
        save_default_dataset(csv_path)
    return csv_path

def load_repair_dataset(csv_path: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the repair cost dataset from CSV.
    """
    path = csv_path or get_default_dataset_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset file not found at: {path}")

    df = pd.read_csv(path)
    validation_report = validate_dataset(df)
    return df, validation_report

def get_train_test_split(
    csv_path: Optional[str] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits the validated dataset into Feature matrices and Target series.
    Target: 'repair_cost'
    """
    df, _ = load_repair_dataset(csv_path)
    
    target_col = "repair_cost"
    feature_cols = [c for c in REQUIRED_COLUMNS if c != target_col]
    
    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test
