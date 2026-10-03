import os
import random
import pandas as pd
import numpy as np
from ai.datasets.schema import REQUIRED_COLUMNS, validate_dataset

# Known device models across smartphones and laptops
DEVICE_MODELS = [
    "iPhone 15 Pro Max",
    "iPhone 15",
    "iPhone 14 Pro",
    "iPhone 13",
    "Samsung Galaxy S23 Ultra",
    "Samsung Galaxy S23",
    "Samsung Galaxy S22",
    "Google Pixel 8 Pro",
    "Google Pixel 7 Pro",
    "MacBook Pro 14 M1",
    "MacBook Air M2",
    "Dell XPS 13 Plus",
    "Dell Inspiron 15",
    "Lenovo ThinkPad X1 Carbon",
    "HP Spectre x360",
]

ISSUE_PROFILES = {
    "screen_cracked": {"parts_range": (80, 240), "labor_range": (45, 90), "duration_range": (1.5, 3.5)},
    "battery_degraded": {"parts_range": (35, 80), "labor_range": (30, 50), "duration_range": (1.0, 2.0)},
    "charging_port_fault": {"parts_range": (20, 50), "labor_range": (35, 65), "duration_range": (1.5, 3.0)},
    "liquid_spill": {"parts_range": (90, 320), "labor_range": (60, 140), "duration_range": (4.0, 12.0)},
    "logic_board_defect": {"parts_range": (120, 450), "labor_range": (80, 180), "duration_range": (5.0, 16.0)},
    "camera_lens_broken": {"parts_range": (40, 110), "labor_range": (35, 60), "duration_range": (1.0, 2.5)},
    "speaker_malfunction": {"parts_range": (25, 55), "labor_range": (30, 45), "duration_range": (1.0, 2.0)},
    "keyboard_failure": {"parts_range": (50, 130), "labor_range": (45, 85), "duration_range": (2.0, 4.5)},
    "thermal_overheating": {"parts_range": (15, 45), "labor_range": (40, 70), "duration_range": (1.5, 3.0)},
}

CONDITIONS = ["poor", "fair", "good", "pristine"]
OUTCOMES = ["SUCCESS", "SUCCESS", "SUCCESS", "SUCCESS", "PARTIAL", "UNREPAIRABLE"]

def generate_historical_dataset(n_samples: int = 1200, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    random.seed(random_seed)

    rows = []
    for _ in range(n_samples):
        model = random.choice(DEVICE_MODELS)
        issue = random.choice(list(ISSUE_PROFILES.keys()))
        prof = ISSUE_PROFILES[issue]
        
        # Laptop multiplier
        is_laptop = any(kw in model.lower() for kw in ["macbook", "dell", "lenovo", "hp"])
        mult = 1.35 if is_laptop else 1.0

        # Device age (months)
        age = round(np.random.exponential(scale=18.0) + 2.0, 1)
        age = min(age, 72.0)

        # Parts & Labor
        parts = round(random.uniform(*prof["parts_range"]) * mult, 2)
        labor = round(random.uniform(*prof["labor_range"]) * mult, 2)
        
        # Duration
        duration = round(random.uniform(*prof["duration_range"]) * mult + random.uniform(-0.3, 0.5), 1)
        duration = max(0.8, duration)

        condition = random.choice(CONDITIONS)
        outcome = random.choice(OUTCOMES)

        # Baseline MSRP and estimated resale value
        base_msrp = 1499.0 if is_laptop else 999.0
        depreciation = max(0.15, 1.0 - (age * 0.018))
        resale_val = round(base_msrp * depreciation * (0.75 if condition == "poor" else 0.9 if condition == "fair" else 1.0), 2)

        # Total repair cost = parts + labor + small platform overhead with slight noise
        overhead = round(random.uniform(5.0, 15.0), 2)
        repair_cost = round(parts + labor + overhead, 2)

        rows.append({
            "device_model": model,
            "device_age": age,
            "issue": issue,
            "repair_cost": repair_cost,
            "parts_cost": parts,
            "labor_cost": labor,
            "condition": condition,
            "resale_value": resale_val,
            "repair_duration": duration,
            "repair_outcome": outcome,
        })

    df = pd.DataFrame(rows)
    return df

def save_default_dataset(output_path: str = None) -> str:
    if output_path is None:
        base_dir = os.path.dirname(__file__)
        output_path = os.path.join(base_dir, "repair_cost_training.csv")
    
    df = generate_historical_dataset(n_samples=1250)
    validate_dataset(df)
    df.to_csv(output_path, index=False)
    print(f"Valid dataset generated and saved to: {output_path} ({len(df)} rows)")
    return output_path

if __name__ == "__main__":
    save_default_dataset()
