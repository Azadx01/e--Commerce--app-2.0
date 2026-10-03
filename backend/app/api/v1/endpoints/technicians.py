from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.technician import TechnicianProfile
from app.models.user import User
from app.schemas.technician import (
    TechnicianResponse,
    TechnicianProfileUpdate,
    TechnicianAdminVerify,
)
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[TechnicianResponse])
def list_technicians(
    db: Session = Depends(get_db),
    device_category: Optional[str] = Query(None, description="Filter by device category (e.g. smartphone, laptop)"),
    specialization: Optional[str] = Query(None, description="Filter by skill or specialization (e.g. Screen, Battery, Micro-soldering)"),
    service_area: Optional[str] = Query(None, description="Filter by service area or location"),
    rating: Optional[float] = Query(None, description="Filter by minimum rating (e.g. 4.0)", ge=0.0, le=5.0),
    availability: Optional[str] = Query(None, description="Filter by availability: available, busy, offline"),
    is_available: Optional[bool] = Query(None, description="Filter by available boolean"),
    verification_status: Optional[str] = Query(None, description="Admin-only filter for verification status"),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    List technicians with filtering.
    Customers and unauthenticated users only see VERIFIED technicians.
    Admins can view all or filter by verification status.
    """
    query = db.query(TechnicianProfile)

    # Access control: Customers and public only see verified technicians
    if not current_user or current_user.role == "customer":
        query = query.filter(TechnicianProfile.verification_status == "verified")
    elif current_user.role == "admin":
        if verification_status:
            query = query.filter(TechnicianProfile.verification_status == verification_status)
    elif current_user.role == "technician":
        # Technicians see verified technicians plus their own profile
        query = query.filter(
            (TechnicianProfile.verification_status == "verified") |
            (TechnicianProfile.user_id == current_user.id)
        )

    # Apply database-level filters
    if service_area:
        query = query.filter(TechnicianProfile.service_area.ilike(f"%{service_area.strip()}%"))

    if rating is not None:
        query = query.filter(TechnicianProfile.rating >= rating)

    if availability:
        query = query.filter(TechnicianProfile.availability.ilike(availability.strip()))

    if is_available is not None:
        query = query.filter(TechnicianProfile.is_available == is_available)

    technicians = query.all()

    # Apply JSON list filters in Python for cross-dialect DB safety
    if device_category:
        cat_clean = device_category.strip().lower()
        technicians = [
            t for t in technicians
            if any(cat_clean in str(c).lower() for c in (t.device_categories or []))
        ]

    if specialization:
        spec_clean = specialization.strip().lower()
        technicians = [
            t for t in technicians
            if any(spec_clean in str(s).lower() for s in (t.skills or []))
        ]

    return technicians[skip : skip + limit]

@router.patch("/profile", response_model=TechnicianResponse)
def update_technician_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: TechnicianProfileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update the authenticated technician's profile.
    Technicians CANNOT modify their own verification_status or rating.
    """
    if current_user.role not in ["technician", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians can manage their technician profile"
        )

    profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
    if not profile:
        # Auto-initialize technician profile if first time
        profile = TechnicianProfile(
            user_id=current_user.id,
            business_name=current_user.name or f"Technician #{current_user.id}",
            verification_status="pending",
            rating=5.0,
            total_reviews=0,
            availability="available",
            is_available=True,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    # Strictly disallow self-verification or rating manipulation
    update_data.pop("verification_status", None)
    update_data.pop("rating", None)
    update_data.pop("total_reviews", None)

    for field, value in update_data.items():
        setattr(profile, field, value)

    # Sync availability with is_available if updated
    if "availability" in update_data:
        profile.is_available = profile.availability.lower() == "available"
    elif "is_available" in update_data:
        profile.availability = "available" if profile.is_available else "offline"

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/{id}", response_model=TechnicianResponse)
def get_technician(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Get technician profile by ID.
    Customers and public can only view verified technicians.
    """
    profile = db.query(TechnicianProfile).filter(TechnicianProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found")

    # Visibility check: unverified technicians are hidden from customers/public
    if profile.verification_status != "verified":
        is_owner = current_user and current_user.id == profile.user_id
        is_admin = current_user and current_user.role == "admin"
        if not (is_owner or is_admin):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found")

    return profile

@router.patch("/{id}/verify", response_model=TechnicianResponse)
def verify_technician(
    *,
    db: Session = Depends(get_db),
    id: int,
    verify_in: TechnicianAdminVerify,
    current_admin: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Admin-only endpoint to verify, reject, or update verification status of a technician.
    """
    profile = db.query(TechnicianProfile).filter(TechnicianProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found")

    profile.verification_status = verify_in.verification_status
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
