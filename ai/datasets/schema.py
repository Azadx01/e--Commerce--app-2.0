from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
import pandas as pd

ALLOWED_ISSUES = [
    "screen_cracked",
    "battery_degraded",
    "charging_port_fault",
    "liquid_spill",
    "logic_board_defect",
    "camera_lens_broken",
    "speaker_malfunction",
    "keyboard_failure",
    "thermal_overheating"
]

ALLOWED_CONDITIONS = ["poor", "fair", "good", "pristine"]
ALLOWED_OUTCOMES = ["SUCCESS", "UNREPAIRABLE", "PARTIAL"]

REQUIRED_COLUMNS = [
    "device_model",
    "device_age",
    "issue",
    "repair_cost",
    "parts_cost",
    "labor_cost",
    "condition",
    "resale_value",
    "repair_duration",
    "repair_outcome"
]

class RepairCostRecord(BaseModel):
    device_model: str = Field(..., description="Model name of the device, e.g. iPhone 14 Pro, Galaxy S23")
    device_age: float = Field(..., ge=0, description="Age of device in months")
    issue: str = Field(..., description="Diagnosed hardware fault")
    repair_cost: float = Field(..., gt=0, description="Total billed repair cost in USD (Target)")
    parts_cost: float = Field(..., ge=0, description="Cost of replacement parts in USD")
    labor_cost: float = Field(..., ge=0, description="Technician labor charges in USD")
    condition: Literal["poor", "fair", "good", "pristine"] = Field(..., description="Exterior condition grade")
    resale_value: float = Field(..., ge=0, description="Current market trade-in / resale value in USD")
    repair_duration: float = Field(..., ge=0, description="Turnaround duration in hours")
    repair_outcome: Literal["SUCCESS", "UNREPAIRABLE", "PARTIAL"] = Field("SUCCESS", description="Outcome of repair")

    @field_validator("issue")
    @classmethod
    def validate_issue(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in ALLOWED_ISSUES:
            # Allow fallback for custom issues but sanitize
            return clean
        return clean

def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates a dataset against the schema requirements.
    Raises ValueError if mandatory schema columns are missing or data types are invalid.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing mandatory schema columns: {missing}")

    if len(df) == 0:
        raise ValueError("Dataset cannot be empty.")

    # Check nulls
    null_counts = df[REQUIRED_COLUMNS].isnull().sum().to_dict()
    total_nulls = sum(null_counts.values())

    # Check numeric constraints
    if (df["repair_cost"] <= 0).any():
        raise ValueError("Target column 'repair_cost' contains non-positive values.")
    if (df["parts_cost"] < 0).any() or (df["labor_cost"] < 0).any():
        raise ValueError("Cost components cannot be negative.")

    return {
        "valid": True,
        "rows": len(df),
        "columns": list(df.columns),
        "total_nulls": total_nulls,
        "null_breakdown": null_counts,
        "issues_distribution": df["issue"].value_counts().to_dict() if "issue" in df.columns else {},
        "models_count": df["device_model"].nunique() if "device_model" in df.columns else 0
    }
