from typing import Dict, Any, Optional

def calculate_decision_metrics(
    device_age: float,
    device_condition: str,
    repair_estimate: float,
    current_estimated_resale_value: float,
    new_device_reference_price: float,
    warranty_status: str,
    user_priority: Optional[str] = "balanced",
) -> Dict[str, Any]:
    """
    Core ReVivo Repair vs Sell vs Replace Decision Engine.
    
    Inputs:
      - device_age: age in months (or years, normalized)
      - device_condition: e.g. 'poor', 'fair', 'good', 'excellent', 'broken'
      - repair_estimate: estimated cost to repair
      - current_estimated_resale_value: current market/as-is trade-in value
      - new_device_reference_price: retail price of comparable new device
      - warranty_status: e.g. 'in_warranty', 'expired', 'out_of_warranty'
      - user_priority: 'budget', 'speed', 'performance', 'sustainability', 'longevity', 'balanced'

    Calculates:
      - repair_ratio = repair_estimate / current_estimated_resale_value
      - repair_vs_new = repair_estimate / new_device_reference_price
      - estimated_value_after_repair

    Returns:
      - repair_option
      - sell_option
      - replace_option
      Each with estimated cost/value, range, explanation, uncertainty/confidence.
      DOES NOT FORCE A WINNER.
    """
    # Normalize age (if <= 8.0, assume user provided years and convert to months)
    age_months = float(device_age * 12.0 if device_age <= 8.0 else device_age)
    age_years = max(age_months / 12.0, 0.2)

    # 1. Calculation: repair_ratio
    # Measures the repair cost relative to current as-is device value
    if current_estimated_resale_value > 0:
        repair_ratio = round(repair_estimate / current_estimated_resale_value, 4)
    else:
        repair_ratio = 1.0

    # 2. Calculation: repair_vs_new
    # Measures the repair cost relative to acquiring a brand-new reference device
    if new_device_reference_price > 0:
        repair_vs_new = round(repair_estimate / new_device_reference_price, 4)
    else:
        repair_vs_new = 0.0

    # 3. Calculation: estimated_value_after_repair
    # Market value of a working refurbished device of this age
    # Used devices typically depreciate at ~18% annually
    depreciated_working_value = new_device_reference_price * (0.82 ** age_years)
    
    # Adding condition adjustment
    cond_lower = device_condition.lower()
    if "excellent" in cond_lower:
        cond_mult = 1.05
    elif "good" in cond_lower:
        cond_mult = 1.0
    elif "fair" in cond_lower:
        cond_mult = 0.92
    else:
        cond_mult = 0.85
    
    post_repair_working_estimate = depreciated_working_value * cond_mult

    # Repair value recovery: device as-is value + retained portion of repair expenditure
    value_recovery = current_estimated_resale_value + (repair_estimate * 0.75)
    
    estimated_value_after_repair = round(
        min(
            max(value_recovery, post_repair_working_estimate, current_estimated_resale_value + 10.0),
            new_device_reference_price * 0.95
        ),
        2
    )

    # Warranty analysis
    warranty_lower = str(warranty_status).lower()
    is_under_warranty = any(w in warranty_lower for w in ["in_warranty", "active", "true", "valid", "covered", "applecare"])

    # Uncertainty & Confidence calculations based on age & market volatility
    # Older devices have higher price variance
    age_confidence_penalty = min(age_years * 0.03, 0.15)
    base_confidence = 0.90 - age_confidence_penalty

    priority_lower = (user_priority or "balanced").lower()

    # --- Option 1: Repair ---
    repair_range_min = round(repair_estimate * 0.90, 2)
    repair_range_max = round(repair_estimate * 1.15, 2)
    repair_conf = round(max(base_confidence - 0.02, 0.70), 2)
    repair_uncertainty = "Low" if repair_conf >= 0.85 else ("Moderate" if repair_conf >= 0.75 else "High")

    repair_explanation = (
        f"Repairing will cost an estimated ${repair_estimate:.2f} ({repair_vs_new * 100:.1f}% of a new replacement). "
        f"This restores functional capability and elevates resale value to approximately ${estimated_value_after_repair:.2f}. "
    )
    if is_under_warranty:
        repair_explanation += "Notice: Device is reported under warranty; official service center or manufacturer claims may offset out-of-pocket costs. "
    if "budget" in priority_lower or "cost" in priority_lower:
        repair_explanation += "Matches cost-conscious priority by avoiding expensive new hardware purchase. "
    elif "sustainability" in priority_lower or "eco" in priority_lower:
        repair_explanation += "Aligns with sustainability priority by preventing e-waste and avoiding manufacturing emissions. "

    repair_option = {
        "action": "repair",
        "name": "Repair Device",
        "estimated_cost": repair_estimate,
        "estimated_value": None,
        "estimated_cost_or_value": repair_estimate,
        "range": {
            "min": repair_range_min,
            "max": repair_range_max
        },
        "range_type": "cost",
        "explanation": repair_explanation.strip(),
        "confidence": repair_conf,
        "uncertainty": repair_uncertainty,
        "key_considerations": [
            f"Repair cost is {repair_vs_new * 100:.1f}% of new device reference price",
            f"Anticipated device value boost to ~${estimated_value_after_repair:.2f}",
            "Preserves personal data without data migration hurdles"
        ]
    }

    # --- Option 2: Sell ---
    sell_range_min = round(current_estimated_resale_value * 0.88, 2)
    sell_range_max = round(current_estimated_resale_value * 1.12, 2)
    sell_conf = round(max(base_confidence - 0.05, 0.65), 2)
    sell_uncertainty = "Low" if sell_conf >= 0.85 else ("Moderate" if sell_conf >= 0.75 else "High")

    sell_explanation = (
        f"Selling as-is recoups an estimated ${current_estimated_resale_value:.2f} in immediate cash or trade-in value "
        f"without risking upfront repair expenditure. "
    )
    if repair_ratio > 0.8:
        sell_explanation += f"Given the high repair ratio ({repair_ratio:.2f}), selling avoids sinking substantial capital into an aging device. "
    if "speed" in priority_lower or "convenience" in priority_lower:
        sell_explanation += "Ideal for speed and convenience if you prefer not waiting for parts or workshop turnaround. "

    sell_option = {
        "action": "sell",
        "name": "Sell / Trade-in As-Is",
        "estimated_cost": None,
        "estimated_value": current_estimated_resale_value,
        "estimated_cost_or_value": current_estimated_resale_value,
        "range": {
            "min": sell_range_min,
            "max": sell_range_max
        },
        "range_type": "value",
        "explanation": sell_explanation.strip(),
        "confidence": sell_conf,
        "uncertainty": sell_uncertainty,
        "key_considerations": [
            f"Liquidates current asset value of ~${current_estimated_resale_value:.2f}",
            "Eliminates repair risks and component lead time",
            "Customer will need alternative device for daily use"
        ]
    }

    # --- Option 3: Replace ---
    replace_net_cost = round(max(new_device_reference_price - current_estimated_resale_value, 0.0), 2)
    replace_range_min = round(new_device_reference_price * 0.90, 2)
    replace_range_max = round(new_device_reference_price * 1.15, 2)
    replace_conf = round(base_confidence, 2)
    replace_uncertainty = "Low" if replace_conf >= 0.85 else ("Moderate" if replace_conf >= 0.75 else "High")

    replace_explanation = (
        f"Acquiring a new comparable device costs ${new_device_reference_price:.2f} "
        f"(or ${replace_net_cost:.2f} net if trading in current device). "
        f"Provides latest technology, fresh battery lifespan, and full manufacturer warranty. "
    )
    if "performance" in priority_lower or "longevity" in priority_lower:
        replace_explanation += "Strongly fits performance and longevity priorities with modernized hardware and extended OS software support. "

    replace_option = {
        "action": "replace",
        "name": "Replace with New Device",
        "estimated_cost": new_device_reference_price,
        "estimated_value": None,
        "estimated_cost_or_value": new_device_reference_price,
        "net_cost_with_trade_in": replace_net_cost,
        "range": {
            "min": replace_range_min,
            "max": replace_range_max
        },
        "range_type": "cost",
        "explanation": replace_explanation.strip(),
        "confidence": replace_conf,
        "uncertainty": replace_uncertainty,
        "key_considerations": [
            f"Initial investment: ${new_device_reference_price:.2f} (Net: ${replace_net_cost:.2f} with trade-in)",
            "Includes brand-new manufacturer warranty and full battery health",
            "Highest capital expenditure among the three pathways"
        ]
    }

    return {
        "repair_ratio": repair_ratio,
        "repair_vs_new": repair_vs_new,
        "estimated_value_after_repair": estimated_value_after_repair,
        "repair_option": repair_option,
        "sell_option": sell_option,
        "replace_option": replace_option,
        # Conveniences / aliases
        "repair": repair_option,
        "sell": sell_option,
        "replace": replace_option,
        "selection_mode": "user_driven_choice",
        "note": "All three pathways are presented objectively. No single option is forced."
    }
