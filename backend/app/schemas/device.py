from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

class DeviceBase(BaseModel):
    category: str = Field(..., pattern="^(smartphone|laptop)$", description="Only smartphones and laptops are permitted for the MVP.")
    brand: str
    model: str
    purchase_date: Optional[datetime] = None
    condition: Optional[str] = None
    status: Optional[str] = "active"

class DeviceCreate(DeviceBase):
    serial_number: Optional[str] = Field(None, description="Sensitive serial number or IMEI to be hashed immediately by backend logic")

class DeviceUpdate(BaseModel):
    condition: Optional[str] = None
    status: Optional[str] = None

class DeviceRead(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# ─── Device Passport & Lifecycle History Schemas ──────────────────────────────

class PassportWarranty(BaseModel):
    is_active: bool
    status: str  # "ACTIVE", "EXPIRED", "EXTENDED"
    valid_until: Optional[datetime] = None
    provider: str
    days_remaining: int
    coverage_details: str

class PassportRepairItem(BaseModel):
    repair_id: int
    service_date: datetime
    issue: str
    parts_replaced: List[str]
    technician_business: str  # Privacy-safe: business / organization name only
    is_verified_technician: bool
    repair_cost: float
    service_warranty_valid_until: Optional[datetime] = None
    service_warranty_duration: Optional[str] = None
    notes: Optional[str] = None

class PassportResaleValuation(BaseModel):
    estimated_market_value: float
    revivo_buyback_estimate: float
    trade_in_value: float
    currency: str = "USD"
    currency_symbol: str = "$"
    condition_grade: str  # "A - Certified", "B - Good", "C - Fair"

class PassportLifecycleEvent(BaseModel):
    event_type: str  # "PURCHASE", "REPAIR", "DIAGNOSTIC", "WARRANTY", "VALUATION"
    date: datetime
    title: str
    description: str
    cost: Optional[float] = None
    icon: str

class DevicePassportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    passport_id: str
    device_id: int
    category: str
    brand: str
    model: str
    masked_identifier: str  # e.g. "ID: #DEV-0042 (Encrypted)"
    purchase_date: Optional[datetime] = None
    initial_condition: Optional[str] = None
    current_health_status: str
    
    warranty: PassportWarranty
    repair_history: List[PassportRepairItem]
    lifecycle_timeline: List[PassportLifecycleEvent]
    resale_valuation: PassportResaleValuation
    
    qr_code_token: str
    verified_at: datetime
