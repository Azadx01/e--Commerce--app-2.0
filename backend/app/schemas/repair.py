from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class RepairStatus(str, Enum):
    REQUESTED = "REQUESTED"
    TECHNICIAN_ASSIGNED = "TECHNICIAN_ASSIGNED"
    DEVICE_RECEIVED = "DEVICE_RECEIVED"
    DIAGNOSIS_PENDING = "DIAGNOSIS_PENDING"
    QUOTE_PENDING = "QUOTE_PENDING"
    CUSTOMER_APPROVED = "CUSTOMER_APPROVED"
    PARTS_PENDING = "PARTS_PENDING"
    REPAIR_IN_PROGRESS = "REPAIR_IN_PROGRESS"
    QUALITY_CHECK = "QUALITY_CHECK"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"

class RepairCreate(BaseModel):
    device_id: int = Field(..., description="ID of customer's registered device")
    technician_id: Optional[int] = Field(None, description="Optional preferred technician ID")
    diagnostic_id: Optional[int] = Field(None, description="Optional diagnostic record ID to link")
    problem_description: str = Field(..., min_length=3, description="Detailed problem description")
    customer_notes: Optional[str] = None

class RepairStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status")
    notes: Optional[str] = Field(None, description="Audit notes or reason for status transition")
    inspection_notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        clean = v.strip().upper()
        allowed = {s.value for s in RepairStatus}
        if clean not in allowed:
            raise ValueError(f"Invalid status: '{v}'. Must be one of: {', '.join(allowed)}")
        return clean

class RepairQuoteSubmit(BaseModel):
    quote_amount: float = Field(..., gt=0, description="Quoted repair cost")
    quote_details: str = Field(..., min_length=3, description="Itemized parts and labor breakdown")
    notes: Optional[str] = None

class RepairQuoteResponse(BaseModel):
    approved: bool = Field(..., description="True to approve quote, False to reject")
    notes: Optional[str] = None

class RepairHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_id: int
    from_status: Optional[str] = None
    to_status: str
    changed_by_user_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class RepairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    device_id: int
    technician_id: Optional[int] = None
    diagnostic_id: Optional[int] = None
    status: str
    problem_description: str
    customer_notes: Optional[str] = None
    inspection_notes: Optional[str] = None
    quote_amount: Optional[float] = None
    quote_details: Optional[str] = None
    quote_approved_at: Optional[datetime] = None
    quote_rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_history: Optional[List[RepairHistoryRead]] = []

# Alias
RepairRead = RepairResponse
