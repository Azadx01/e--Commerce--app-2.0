import hashlib
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead, DevicePassportResponse
from app.services.passport_service import build_device_passport
from app.api import deps

router = APIRouter()

def hash_identifier(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()

@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(
    *,
    db: Session = Depends(get_db),
    device_in: DeviceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Explicit mapping to drop raw serial number out
    device_data = device_in.model_dump(exclude={"serial_number"})
    
    # Hash secure identifier securely if provided 
    if device_in.serial_number:
        device_data["serial_number_hash"] = hash_identifier(device_in.serial_number)
        
    device = Device(**device_data, user_id=current_user.id)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

@router.get("", response_model=List[DeviceRead])
def read_devices(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Safely query ONLY current_user devices (Hardcoded protection block)
    devices = db.query(Device).filter(Device.user_id == current_user.id).offset(skip).limit(limit).all()
    return devices

@router.get("/{id}/passport", response_model=DevicePassportResponse)
def get_device_passport(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve consolidated Device Passport and Lifecycle History.
    Includes purchase date, verified repair history, replaced parts, warranty status, and resale valuation.
    Does not expose sensitive personal information publicly.
    """
    device = db.query(Device).filter(Device.id == id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # Authorization check
    if current_user.role == "customer":
        if device.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this device passport")
    elif current_user.role == "technician":
        from app.models.technician import TechnicianProfile
        from app.models.repair import Repair
        tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_prof.id if tech_prof else -1
        is_assigned = db.query(Repair).filter(
            Repair.device_id == device.id,
            Repair.technician_id == tech_id
        ).first() is not None
        if not is_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Technicians can only access passports for assigned customer devices")
    elif current_user.role != "admin":
        if device.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    passport = build_device_passport(db=db, device=device)
    return passport

@router.get("/{id}", response_model=DeviceRead)
def read_device(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    device = db.query(Device).filter(Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if current_user.role == "customer":
        if device.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "technician":
        from app.models.technician import TechnicianProfile
        from app.models.repair import Repair
        tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_prof.id if tech_prof else -1
        is_assigned = db.query(Repair).filter(
            Repair.device_id == device.id,
            Repair.technician_id == tech_id
        ).first() is not None
        if not is_assigned:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role != "admin":
        if device.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return device

@router.patch("/{id}", response_model=DeviceRead)
def update_device(
    *,
    db: Session = Depends(get_db),
    id: int,
    device_in: DeviceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    device = db.query(Device).filter(Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    update_data = device_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
        
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{id}", response_model=DeviceRead)
def delete_device(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    device = db.query(Device).filter(Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db.delete(device)
    db.commit()
    return device

