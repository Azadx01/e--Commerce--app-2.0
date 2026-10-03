from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.device import Device
from app.models.user import User
from app.schemas.decision import DecisionInput, DecisionResponse
from app.services.decision_engine import calculate_decision_metrics
from app.api import deps

router = APIRouter()

@router.post("", response_model=DecisionResponse, status_code=status.HTTP_200_OK)
def evaluate_decision(
    *,
    db: Session = Depends(get_db),
    decision_in: DecisionInput,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Repair vs Sell vs Replace Decision Engine.
    Evaluates:
      - repair_ratio
      - repair_vs_new
      - estimated_value_after_repair
      - repair_option (cost/value, range, explanation, uncertainty/confidence)
      - sell_option (cost/value, range, explanation, uncertainty/confidence)
      - replace_option (cost/value, range, explanation, uncertainty/confidence)
    DOES NOT force a winner, empowering user choice.
    """
    if decision_in.device_id is not None:
        device = db.query(Device).filter(Device.id == decision_in.device_id).first()
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        
        if current_user and current_user.role == "customer" and device.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access another user's device"
            )

    # Compute options and calculations
    metrics_result = calculate_decision_metrics(
        device_age=decision_in.device_age,
        device_condition=decision_in.device_condition,
        repair_estimate=decision_in.repair_estimate,
        current_estimated_resale_value=decision_in.current_estimated_resale_value,
        new_device_reference_price=decision_in.new_device_reference_price,
        warranty_status=decision_in.warranty_status,
        user_priority=decision_in.user_priority,
    )

    # Persist decision log
    decision_record = Decision(
        device_id=decision_in.device_id,
        device_age=decision_in.device_age,
        device_condition=decision_in.device_condition,
        repair_estimate=decision_in.repair_estimate,
        current_estimated_resale_value=decision_in.current_estimated_resale_value,
        new_device_reference_price=decision_in.new_device_reference_price,
        warranty_status=decision_in.warranty_status,
        user_priority=decision_in.user_priority,
        repair_ratio=metrics_result["repair_ratio"],
        repair_vs_new=metrics_result["repair_vs_new"],
        estimated_value_after_repair=metrics_result["estimated_value_after_repair"],
        result_payload=metrics_result,
    )
    db.add(decision_record)
    db.commit()
    db.refresh(decision_record)

    response_data = dict(metrics_result)
    response_data["id"] = decision_record.id
    response_data["device_id"] = decision_record.device_id
    response_data["created_at"] = decision_record.created_at

    return response_data
