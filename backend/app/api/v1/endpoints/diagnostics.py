from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.diagnostic import Diagnostic
from app.models.device import Device
from app.models.user import User
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticResponse
from app.services.diagnosis_engine import evaluate_device_diagnosis
from app.api import deps

router = APIRouter()

@router.post("", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostic(
    *,
    db: Session = Depends(get_db),
    diagnostic_in: DiagnosticCreate,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Submit device symptoms and optional images for rule-based preliminary diagnosis.
    Returns:
      - possible issue
      - estimated severity
      - recommended next action
      - confidence
      - requirement for technician inspection
    """
    device_category: Optional[str] = None

    if diagnostic_in.device_id is not None:
        device = db.query(Device).filter(Device.id == diagnostic_in.device_id).first()
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        
        # If user is authenticated as customer, verify ownership of device
        if current_user and current_user.role == "customer" and device.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to diagnose another user's device"
            )
        device_category = device.category

    # Run structured rule-based diagnosis engine
    eval_result = evaluate_device_diagnosis(
        selected_symptoms=diagnostic_in.selected_symptoms,
        reported_problem=diagnostic_in.reported_problem,
        image_references=diagnostic_in.image_references,
        device_category=device_category,
    )

    diagnostic = Diagnostic(
        device_id=diagnostic_in.device_id,
        reported_problem=diagnostic_in.reported_problem,
        selected_symptoms=diagnostic_in.selected_symptoms,
        image_references=diagnostic_in.image_references or [],
        diagnosis_result=eval_result,
        confidence=eval_result["confidence"],
        engine_version=eval_result["engine_version"],
    )

    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic

@router.get("/{id}", response_model=DiagnosticResponse, status_code=status.HTTP_200_OK)
def read_diagnostic(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Retrieve diagnosis record by ID.
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == id).first()
    if not diagnostic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic record not found")

    # If customer is authenticated and diagnostic is associated with a device, enforce data isolation
    if current_user and current_user.role == "customer" and diagnostic.device_id:
        device = db.query(Device).filter(Device.id == diagnostic.device_id).first()
        if device and device.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return diagnostic
