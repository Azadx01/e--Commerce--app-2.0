from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class QuoteStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"
    SUPERSEDED = "SUPERSEDED"

class QuoteCreate(BaseModel):
    diagnosis: str = Field(..., min_length=3, description="Technical diagnosis & findings")
    labor_cost: float = Field(default=0.0, ge=0.0, description="Labor cost")
    parts_cost: float = Field(default=0.0, ge=0.0, description="Replacement parts cost")
    other_fees: float = Field(default=0.0, ge=0.0, description="Other allowed fees (e.g. disposal, expedited delivery)")
    expected_completion_time: str = Field(..., min_length=1, description="Expected turnaround time (e.g. 2 business days)")
    warranty_duration: str = Field(..., min_length=1, description="Warranty coverage (e.g. 90 days on parts and labor)")
    notes: Optional[str] = Field(None, description="Additional technician notes")
    before_repair_images: Optional[List[str]] = Field(default_factory=list, description="Pre-repair photos for documentation")
    is_change_request: Optional[bool] = Field(False, description="Flag indicating supplemental price increase or change request")

    @property
    def computed_total(self) -> float:
        return round(self.labor_cost + self.parts_cost + self.other_fees, 2)

class QuoteClarificationRequest(BaseModel):
    message: str = Field(..., min_length=2, description="Question or clarification request from customer")

class QuoteClarificationResponse(BaseModel):
    response: str = Field(..., min_length=2, description="Answer or response from technician")

class QuoteDecision(BaseModel):
    customer_notes: Optional[str] = Field(None, description="Optional customer notes upon approval/rejection")
    approved: Optional[bool] = Field(None, description="Optional flag for approval or rejection")

class QuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_id: int
    technician_id: Optional[int] = None
    version: int
    is_change_request: bool
    
    diagnosis: str
    labor_cost: float
    parts_cost: float
    other_fees: float
    total_amount: float
    expected_completion_time: str
    warranty_duration: str
    notes: Optional[str] = None
    before_repair_images: Optional[List[str]] = []
    
    status: str
    customer_notes: Optional[str] = None
    clarification_message: Optional[str] = None
    clarification_response: Optional[str] = None
    clarification_requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Alias
QuoteRead = QuoteResponse
