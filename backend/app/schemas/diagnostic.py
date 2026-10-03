from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.diagnosis_engine import SymptomCategory

class DiagnosticBase(BaseModel):
    device_id: Optional[int] = Field(None, description="Optional ID of registered device to link diagnostic record")
    reported_problem: Optional[str] = Field(None, description="Customer-reported problem or description")
    selected_symptoms: List[str] = Field(
        ...,
        description="Symptoms chosen from: Battery, Screen, Charging, Heating, Performance, Keyboard, Camera, Speaker, Network, Other"
    )
    image_references: Optional[List[str]] = Field(
        default_factory=list,
        description="Optional image URLs, storage keys, or references"
    )

    @field_validator("selected_symptoms")
    @classmethod
    def validate_and_normalize_symptoms(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one symptom must be selected.")
        
        allowed_map = {item.value.lower(): item.value for item in SymptomCategory}
        normalized = []
        for symptom in v:
            clean = symptom.strip().lower()
            if clean not in allowed_map:
                valid_options = ", ".join([item.value for item in SymptomCategory])
                raise ValueError(f"Invalid symptom: '{symptom}'. Must be one of: {valid_options}")
            normalized.append(allowed_map[clean])
        # Return unique preserved order
        return list(dict.fromkeys(normalized))

class DiagnosticCreate(DiagnosticBase):
    pass

class DiagnosticResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: Optional[int] = None
    reported_problem: Optional[str] = None
    selected_symptoms: List[str]
    image_references: Optional[List[str]] = []
    
    # Core system return fields
    possible_issue: str
    estimated_severity: str
    recommended_next_action: str
    recommended_action: Optional[str] = None
    confidence: float
    requirement_for_technician_inspection: bool
    requires_technician_inspection: Optional[bool] = None

    # Metadata & Results
    diagnosis_result: Dict[str, Any]
    engine_version: str
    created_at: datetime
    disclaimer: str

# Alias for flexibility
DiagnosticRead = DiagnosticResponse
