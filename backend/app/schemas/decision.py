from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class OptionRange(BaseModel):
    min: float
    max: float

class DecisionOption(BaseModel):
    action: str
    name: str
    estimated_cost: Optional[float] = None
    estimated_value: Optional[float] = None
    estimated_cost_or_value: float
    range: OptionRange
    range_type: Optional[str] = None
    explanation: str
    confidence: float
    uncertainty: str
    key_considerations: Optional[List[str]] = Field(default_factory=list)

class DecisionInput(BaseModel):
    device_age: float = Field(..., description="Device age in months (e.g. 18) or years (e.g. 1.5)")
    device_condition: str = Field(..., description="Condition: e.g. poor, fair, good, excellent, broken")
    repair_estimate: float = Field(..., description="Estimated cost of repairs", ge=0)
    current_estimated_resale_value: float = Field(..., description="Current market/as-is resale value", ge=0)
    new_device_reference_price: float = Field(..., description="Reference price of comparable new device", ge=0)
    warranty_status: str = Field(..., description="Warranty status: in_warranty, expired, out_of_warranty, etc.")
    user_priority: Optional[str] = Field("balanced", description="User priority: cost, budget, speed, performance, sustainability, balanced")
    device_id: Optional[int] = Field(None, description="Optional registered device ID to associate")

    @model_validator(mode="before")
    @classmethod
    def map_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map aliases if alternative keys are provided
            if "device_age" not in data and "device_age_months" in data:
                data["device_age"] = data["device_age_months"]
            elif "device_age" not in data and "age" in data:
                data["device_age"] = data["age"]
            
            if "current_estimated_resale_value" not in data:
                if "current_resale_value" in data:
                    data["current_estimated_resale_value"] = data["current_resale_value"]
                elif "resale_value" in data:
                    data["current_estimated_resale_value"] = data["resale_value"]

            if "new_device_reference_price" not in data:
                if "new_device_price" in data:
                    data["new_device_reference_price"] = data["new_device_price"]
                elif "reference_price" in data:
                    data["new_device_reference_price"] = data["reference_price"]

            if "user_priority" not in data and "priority" in data:
                data["user_priority"] = data["priority"]

            if "warranty_status" not in data and "warranty" in data:
                data["warranty_status"] = str(data["warranty"])
        return data

class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    device_id: Optional[int] = None

    # Three core calculations
    repair_ratio: float
    repair_vs_new: float
    estimated_value_after_repair: float

    # Three options
    repair_option: DecisionOption
    sell_option: DecisionOption
    replace_option: DecisionOption

    # Aliases for options
    repair: Optional[DecisionOption] = None
    sell: Optional[DecisionOption] = None
    replace: Optional[DecisionOption] = None

    selection_mode: str = "user_driven_choice"
    note: str = "All three pathways are presented objectively. No single option is forced."
    created_at: Optional[datetime] = None
