from typing import Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.repair import Repair, RepairHistory
from app.models.device import Device
from app.models.technician import TechnicianProfile
from app.models.diagnostic import Diagnostic
from app.models.user import User
from app.schemas.repair import (
    RepairCreate,
    RepairResponse,
    RepairRead,
    RepairStatusUpdate,
    RepairQuoteSubmit,
    RepairQuoteResponse,
    RepairHistoryRead,
    RepairStatus,
)
from app.services.repair_service import transition_repair_status
from app.api import deps

router = APIRouter()

@router.post("", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
def create_repair_request(
    *,
    db: Session = Depends(get_db),
    repair_in: RepairCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Customer creates a new repair request (Status: REQUESTED).
    Logs initial audit history.
    """
    # 1. Verify device ownership
    device = db.query(Device).filter(Device.id == repair_in.device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if current_user.role == "customer" and device.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this device")

    # 2. Verify optional technician if specified
    if repair_in.technician_id is not None:
        tech = db.query(TechnicianProfile).filter(TechnicianProfile.id == repair_in.technician_id).first()
        if not tech:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found")

    # 3. Verify optional diagnostic if specified
    if repair_in.diagnostic_id is not None:
        diag = db.query(Diagnostic).filter(Diagnostic.id == repair_in.diagnostic_id).first()
        if not diag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic record not found")

    repair = Repair(
        customer_id=current_user.id,
        device_id=repair_in.device_id,
        technician_id=repair_in.technician_id,
        diagnostic_id=repair_in.diagnostic_id,
        status=RepairStatus.REQUESTED.value,
        problem_description=repair_in.problem_description,
        customer_notes=repair_in.customer_notes,
    )
    db.add(repair)
    db.commit()
    db.refresh(repair)

    # Initial audit log entry
    history = RepairHistory(
        repair_id=repair.id,
        from_status=None,
        to_status=RepairStatus.REQUESTED.value,
        changed_by_user_id=current_user.id,
        notes="Repair request submitted by customer",
    )
    db.add(history)
    db.commit()
    db.refresh(repair)

    # Emit notification event
    try:
        from app.services.notification_service import NotificationService
        device_label = f"{device.brand} {device.model}".strip() or "Device"
        NotificationService.notify_repair_request_created(
            db=db,
            user_id=current_user.id,
            repair_id=repair.id,
            device_name=device_label
        )
    except Exception:
        pass

    return repair

@router.get("", response_model=List[RepairResponse])
def list_repairs(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    device_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List repairs with role-based filtering:
      - Customers see only their own repairs.
      - Technicians see assigned repairs or unassigned REQUESTED repairs.
      - Admins see all repairs.
    """
    query = db.query(Repair)

    if current_user.role == "customer":
        query = query.filter(Repair.customer_id == current_user.id)
    elif current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_profile.id if tech_profile else -1
        query = query.filter(
            (Repair.technician_id == tech_id) |
            ((Repair.status == RepairStatus.REQUESTED.value) & (Repair.technician_id.is_(None)))
        )

    if status_filter:
        query = query.filter(Repair.status == status_filter.upper())
    if device_id:
        query = query.filter(Repair.device_id == device_id)

    repairs = query.order_by(Repair.created_at.desc()).offset(skip).limit(limit).all()
    return repairs

@router.get("/{id}", response_model=RepairResponse)
def get_repair(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve single repair by ID with permission checks.
    """
    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    # Permission check
    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    elif current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_profile.id if tech_profile else -1
        if repair.technician_id != tech_id and not (repair.status == RepairStatus.REQUESTED.value and repair.technician_id is None):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return repair

@router.post("/{id}/accept", response_model=RepairResponse)
def accept_repair_request(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Technician accepts an open repair request (REQUESTED -> TECHNICIAN_ASSIGNED).
    """
    if current_user.role not in ["technician", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only technicians can accept repair requests")

    tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
    if not tech_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Technician profile must be created first")

    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    repair.technician_id = tech_profile.id
    repair = transition_repair_status(
        db=db,
        repair=repair,
        target_status=RepairStatus.TECHNICIAN_ASSIGNED.value,
        changed_by_user_id=current_user.id,
        notes=f"Technician '{tech_profile.name}' accepted the repair request.",
    )
    return repair

@router.post("/{id}/quote", response_model=RepairResponse)
def submit_repair_quote(
    *,
    db: Session = Depends(get_db),
    id: int,
    quote_in: RepairQuoteSubmit,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Technician submits an inspection quote (-> QUOTE_PENDING).
    """
    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        if not tech_profile or repair.technician_id != tech_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned technician")

    repair.quote_amount = quote_in.quote_amount
    repair.quote_details = quote_in.quote_details
    repair = transition_repair_status(
        db=db,
        repair=repair,
        target_status=RepairStatus.QUOTE_PENDING.value,
        changed_by_user_id=current_user.id,
        notes=f"Technician submitted quote: ${quote_in.quote_amount:.2f}. {quote_in.notes or ''}".strip(),
    )
    return repair

@router.post("/{id}/quote/respond", response_model=RepairResponse)
def respond_to_quote(
    *,
    db: Session = Depends(get_db),
    id: int,
    response_in: RepairQuoteResponse,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Customer approves or rejects the repair quote.
    Approved -> CUSTOMER_APPROVED
    Rejected -> CANCELLED
    """
    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")

    if repair.status != RepairStatus.QUOTE_PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending quote to respond to")

    if response_in.approved:
        repair.quote_approved_at = datetime.now(timezone.utc)
        repair = transition_repair_status(
            db=db,
            repair=repair,
            target_status=RepairStatus.CUSTOMER_APPROVED.value,
            changed_by_user_id=current_user.id,
            notes=f"Customer approved quote of ${repair.quote_amount or 0:.2f}. {response_in.notes or ''}".strip(),
        )
    else:
        repair.quote_rejected_at = datetime.now(timezone.utc)
        repair = transition_repair_status(
            db=db,
            repair=repair,
            target_status=RepairStatus.CANCELLED.value,
            changed_by_user_id=current_user.id,
            notes=f"Customer rejected quote - cancelled. {response_in.notes or ''}".strip(),
        )

    return repair

@router.patch("/{id}/status", response_model=RepairResponse)
def update_repair_status(
    *,
    db: Session = Depends(get_db),
    id: int,
    status_in: RepairStatusUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update repair status with transition validation and audit logging.
    """
    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    target_status = status_in.status.upper()

    # Role and authorization validation
    if current_user.role == "customer":
        if repair.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your repair")
        if target_status not in [RepairStatus.CANCELLED.value, RepairStatus.DISPUTED.value, RepairStatus.CLOSED.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Customers cannot move repair to '{target_status}'"
            )
    elif current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        if not tech_profile or repair.technician_id != tech_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned technician")

    if status_in.inspection_notes:
        repair.inspection_notes = status_in.inspection_notes

    repair = transition_repair_status(
        db=db,
        repair=repair,
        target_status=target_status,
        changed_by_user_id=current_user.id,
        notes=status_in.notes,
        is_admin=(current_user.role == "admin"),
    )
    return repair

@router.get("/{id}/history", response_model=List[RepairHistoryRead])
def get_repair_history(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve full audit status history trail for a repair.
    """
    repair = db.query(Repair).filter(Repair.id == id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    history = db.query(RepairHistory).filter(RepairHistory.repair_id == id).order_by(RepairHistory.created_at.asc()).all()
    return history
