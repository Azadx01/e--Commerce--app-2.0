from typing import Optional, Set
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.repair import Repair, RepairHistory
from app.schemas.repair import RepairStatus

VALID_TRANSITIONS = {
    RepairStatus.REQUESTED.value: {
        RepairStatus.TECHNICIAN_ASSIGNED.value,
        RepairStatus.CANCELLED.value,
    },
    RepairStatus.TECHNICIAN_ASSIGNED.value: {
        RepairStatus.DEVICE_RECEIVED.value,
        RepairStatus.DIAGNOSIS_PENDING.value,
        RepairStatus.QUOTE_PENDING.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.DEVICE_RECEIVED.value: {
        RepairStatus.DIAGNOSIS_PENDING.value,
        RepairStatus.QUOTE_PENDING.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.DIAGNOSIS_PENDING.value: {
        RepairStatus.QUOTE_PENDING.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.QUOTE_PENDING.value: {
        RepairStatus.CUSTOMER_APPROVED.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.CUSTOMER_APPROVED.value: {
        RepairStatus.PARTS_PENDING.value,
        RepairStatus.REPAIR_IN_PROGRESS.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.PARTS_PENDING.value: {
        RepairStatus.REPAIR_IN_PROGRESS.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.REPAIR_IN_PROGRESS.value: {
        RepairStatus.QUALITY_CHECK.value,
        RepairStatus.PARTS_PENDING.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.QUALITY_CHECK.value: {
        RepairStatus.READY_FOR_DELIVERY.value,
        RepairStatus.REPAIR_IN_PROGRESS.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.READY_FOR_DELIVERY.value: {
        RepairStatus.DELIVERED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.DELIVERED.value: {
        RepairStatus.CLOSED.value,
        RepairStatus.DISPUTED.value,
    },
    RepairStatus.DISPUTED.value: {
        RepairStatus.REPAIR_IN_PROGRESS.value,
        RepairStatus.CANCELLED.value,
        RepairStatus.CLOSED.value,
    },
    RepairStatus.CLOSED.value: set(),
    RepairStatus.CANCELLED.value: set(),
}

def validate_status_transition(current_status: str, target_status: str, is_admin: bool = False) -> None:
    """
    Validates state machine transitions.
    Raises HTTPException 400 if the transition is invalid.
    """
    if current_status == target_status:
        return

    allowed_next_statuses: Set[str] = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_next_statuses:
        allowed_str = ", ".join(allowed_next_statuses) if allowed_next_statuses else "None (terminal state)"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{target_status}'. Allowed transitions: [{allowed_str}]."
        )

def transition_repair_status(
    db: Session,
    repair: Repair,
    target_status: str,
    changed_by_user_id: int,
    notes: Optional[str] = None,
    is_admin: bool = False,
) -> Repair:
    """
    Executes validated status transition and creates audit history entry.
    """
    from_status = repair.status
    if from_status != target_status:
        validate_status_transition(from_status, target_status, is_admin=is_admin)
        repair.status = target_status

    # Record audit log entry
    history_entry = RepairHistory(
        repair_id=repair.id,
        from_status=from_status,
        to_status=target_status,
        changed_by_user_id=changed_by_user_id,
        notes=notes,
    )
    db.add(history_entry)
    db.add(repair)
    db.commit()
    db.refresh(repair)

    # Emit domain event notifications
    try:
        from app.services.notification_service import NotificationService
        from app.models.device import Device
        from app.models.technician import TechnicianProfile

        device = db.query(Device).filter(Device.id == repair.device_id).first()
        dev_label = f"{device.brand} {device.model}".strip() if device else "Device"
        
        tech_name = "Assigned Technician"
        if repair.technician_id:
            tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.id == repair.technician_id).first()
            if tech_prof and tech_prof.business_name:
                tech_name = tech_prof.business_name

        if target_status == RepairStatus.TECHNICIAN_ASSIGNED.value:
            NotificationService.notify_technician_accepted(
                db=db,
                user_id=repair.customer_id,
                repair_id=repair.id,
                technician_name=tech_name,
                device_name=dev_label
            )
        elif target_status == RepairStatus.PARTS_PENDING.value:
            NotificationService.notify_parts_required(
                db=db,
                user_id=repair.customer_id,
                repair_id=repair.id,
                part_name="Required Hardware Module",
                device_name=dev_label
            )
        elif target_status == RepairStatus.REPAIR_IN_PROGRESS.value:
            NotificationService.notify_repair_started(
                db=db,
                user_id=repair.customer_id,
                repair_id=repair.id,
                device_name=dev_label,
                technician_name=tech_name
            )
        elif target_status in [RepairStatus.READY_FOR_DELIVERY.value, RepairStatus.DELIVERED.value, RepairStatus.CLOSED.value]:
            if from_status != target_status:
                NotificationService.notify_repair_completed(
                    db=db,
                    user_id=repair.customer_id,
                    repair_id=repair.id,
                    device_name=dev_label
                )
                NotificationService.notify_warranty_started(
                    db=db,
                    user_id=repair.customer_id,
                    device_name=dev_label,
                    duration_text="180 days",
                    expiry_date="in 6 months"
                )
    except Exception:
        pass

    return repair
