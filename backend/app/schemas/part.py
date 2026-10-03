from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

class PartCondition(str, Enum):
    OEM = "OEM"
    COMPATIBLE_THIRD_PARTY = "COMPATIBLE_THIRD_PARTY"
    USED_TESTED = "USED_TESTED"

class CompatibilityRule(BaseModel):
    category: Optional[str] = Field(None, description="e.g. smartphone or laptop")
    brand: Optional[str] = Field(None, description="e.g. Apple, Samsung, Google")
    models: List[str] = Field(default_factory=list, description="List of compatible model names or numbers")
    notes: Optional[str] = Field(None, description="Special installation or fitment notes")

class PartBase(BaseModel):
    name: str = Field(..., min_length=2, description="Part name")
    sku: str = Field(..., min_length=2, description="Unique SKU code")
    part_type: str = Field(..., min_length=2, description="e.g. Screen, Battery, Charging Port, Camera, Keyboard")
    manufacturer: str = Field(..., min_length=2, description="Part manufacturer or brand")
    condition: PartCondition = Field(..., description="Part condition: OEM, COMPATIBLE_THIRD_PARTY, or USED_TESTED")
    price: float = Field(..., gt=0, description="Price in USD")
    warranty: str = Field(..., min_length=1, description="Warranty period e.g. 180 days, 1 year")
    stock: int = Field(default=0, ge=0, description="Available inventory quantity")
    seller: str = Field(..., min_length=2, description="Seller or supplier name")
    compatibility: List[CompatibilityRule] = Field(
        default_factory=list,
        description="List of device category, brand, and model compatibility rules"
    )
    description: Optional[str] = Field(None, description="Detailed component specifications")
    image_url: Optional[str] = Field(None, description="Product image link")
    rating: Optional[float] = Field(default=4.8, ge=0.0, le=5.0, description="User or quality rating")
    is_active: Optional[bool] = Field(default=True, description="Whether part is active for sale")

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    warranty: Optional[str] = None
    stock: Optional[int] = None
    condition: Optional[PartCondition] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PartResponse(PartBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class PartListResponse(BaseModel):
    items: List[PartResponse]
    total: int
    skip: int
    limit: int
