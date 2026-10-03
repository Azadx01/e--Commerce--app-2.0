from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Any
from datetime import datetime

class TechnicianBase(BaseModel):
    business_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    years_of_experience: Optional[int] = Field(default=1, ge=0)
    profile_picture_url: Optional[str] = None
    skills: List[str] = Field(default_factory=list, description="Skills e.g. Screen Replacement, Battery, Micro-soldering")
    device_categories: List[str] = Field(default_factory=list, description="Supported categories e.g. smartphone, laptop")
    service_area: str = Field(default="Metro Area", description="Service area / city")
    service_radius_km: Optional[float] = Field(default=25.0, ge=0)
    availability: str = Field(default="available", description="available, busy, offline")
    is_available: bool = Field(default=True)
    hourly_rate: Optional[float] = Field(None, ge=0)

class TechnicianProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    profile_picture_url: Optional[str] = None
    skills: Optional[List[str]] = None
    device_categories: Optional[List[str]] = None
    service_area: Optional[str] = None
    service_radius_km: Optional[float] = Field(None, ge=0)
    availability: Optional[str] = None
    is_available: Optional[bool] = None
    hourly_rate: Optional[float] = Field(None, ge=0)

class TechnicianAdminVerify(BaseModel):
    verification_status: str = Field(..., pattern="^(verified|rejected|pending)$")

class TechnicianResponse(TechnicianBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str = ""
    email: str = ""
    verification_status: str
    rating: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_user_fields(cls, data: Any) -> Any:
        if hasattr(data, "user") and data.user:
            # SQLAlchemy model object
            name = data.name if hasattr(data, "name") else (data.user.name or "")
            email = data.email if hasattr(data, "email") else (data.user.email or "")
            return {
                "id": data.id,
                "user_id": data.user_id,
                "name": name,
                "email": email,
                "business_name": data.business_name,
                "bio": data.bio,
                "phone": data.phone,
                "years_of_experience": data.years_of_experience,
                "profile_picture_url": data.profile_picture_url,
                "skills": data.skills or [],
                "device_categories": data.device_categories or [],
                "service_area": data.service_area,
                "service_radius_km": data.service_radius_km,
                "verification_status": data.verification_status,
                "rating": data.rating,
                "total_reviews": data.total_reviews,
                "availability": data.availability,
                "is_available": data.is_available,
                "hourly_rate": data.hourly_rate,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data

# Alias
TechnicianRead = TechnicianResponse
