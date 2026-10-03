from typing import Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.repair import Repair, RepairHistory
from app.models.quote import Quote
from app.models.technician import TechnicianProfile
from app.models.user import User
from app.schemas.quote import (
    QuoteCreate,
    QuoteResponse,
    QuoteRead,
    QuoteClarificationRequest,
    QuoteClarificationResponse,
    QuoteDecision,
    QuoteStatus,
)
from app.schemas.repair import RepairStatus
from app.services.repair_service import transition_repair_status
from app.api import deps

router = APIRouter()

@router.post("/repairs/{repair_id}/quotes", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_repair_quote(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_in: QuoteCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Technician submits an initial quote or a supplemental change request.
    A technician must NOT increase the final price without customer approval.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    tech_profile = None
    if current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        if not tech_profile or repair.technician_id != tech_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned technician for this repair")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only technicians can create quotes")

    # Determine version and change request status
    previous_quotes = db.query(Quote).filter(Quote.repair_id == repair_id).order_by(Quote.version.desc()).all()
    version = len(previous_quotes) + 1
    is_change_request = quote_in.is_change_request or (version > 1)

    total = round(quote_in.labor_cost + quote_in.parts_cost + quote_in.other_fees, 2)

    # If new quote/change request, mark any old unapproved PENDING quotes as SUPERSEDED
    for q in previous_quotes:
        if q.status in [QuoteStatus.PENDING.value, QuoteStatus.CLARIFICATION_REQUESTED.value]:
            q.status = QuoteStatus.SUPERSEDED.value
            db.add(q)

    quote = Quote(
        repair_id=repair_id,
        technician_id=repair.technician_id,
        version=version,
        is_change_request=is_change_request,
        diagnosis=quote_in.diagnosis,
        labor_cost=quote_in.labor_cost,
        parts_cost=quote_in.parts_cost,
        other_fees=quote_in.other_fees,
        total_amount=total,
        expected_completion_time=quote_in.expected_completion_time,
        warranty_duration=quote_in.warranty_duration,
        notes=quote_in.notes,
        before_repair_images=quote_in.before_repair_images or [],
        status=QuoteStatus.PENDING.value,
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)

    # Note: repair.quote_amount is NOT updated yet until customer approves!
    # Update repair workflow status to QUOTE_PENDING
    if repair.status != RepairStatus.QUOTE_PENDING.value:
        try:
            transition_repair_status(
                db=db,
                repair=repair,
                target_status=RepairStatus.QUOTE_PENDING.value,
                changed_by_user_id=current_user.id,
                notes=f"Submitted Quote v{version} (${total:.2f}) - pending customer approval.",
                is_admin=(current_user.role == "admin"),
            )
        except HTTPException:
            # If repair was already in progress and this is a supplemental change request, record history log
            history = RepairHistory(
                repair_id=repair.id,
                from_status=repair.status,
                to_status=repair.status,
                changed_by_user_id=current_user.id,
                notes=f"Change Request Quote v{version} submitted for ${total:.2f}. Awaiting customer approval.",
            )
            db.add(history)
            db.commit()

    # Emit notification to customer
    try:
        from app.services.notification_service import NotificationService
        from app.models.device import Device
        device = db.query(Device).filter(Device.id == repair.device_id).first()
        dev_label = f"{device.brand} {device.model}".strip() if device else "Device"
        NotificationService.notify_quote_received(
            db=db,
            user_id=repair.customer_id,
            repair_id=repair.id,
            quote_id=quote.id,
            total_amount=quote.total_amount,
            device_name=dev_label
        )
    except Exception:
        pass

    return quote

@router.get("/repairs/{repair_id}/quotes", response_model=List[QuoteResponse])
def get_quote_history(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve complete quote history (all versions and change requests) for a repair.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")
    elif current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        if not tech_profile or repair.technician_id != tech_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned technician")

    quotes = db.query(Quote).filter(Quote.repair_id == repair_id).order_by(Quote.version.asc()).all()
    return quotes

@router.get("/repairs/{repair_id}/quotes/{quote_id}", response_model=QuoteResponse)
def get_single_quote(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific quote by ID.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")

    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.repair_id == repair_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    return quote

@router.post("/repairs/{repair_id}/quotes/{quote_id}/approve", response_model=QuoteResponse)
def approve_quote(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_id: int,
    decision_in: Optional[QuoteDecision] = Body(default=None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:

    """
    Customer approves the quote.
    Updates quote status to APPROVED, updates repair.quote_amount to approved price,
    and advances repair workflow.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")

    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.repair_id == repair_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    if quote.status not in [QuoteStatus.PENDING.value, QuoteStatus.CLARIFICATION_REQUESTED.value]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot approve quote with status '{quote.status}'")

    # Mark prior quotes as SUPERSEDED
    prior_quotes = db.query(Quote).filter(Quote.repair_id == repair_id, Quote.id != quote_id).all()
    for q in prior_quotes:
        if q.status in [QuoteStatus.APPROVED.value, QuoteStatus.PENDING.value, QuoteStatus.CLARIFICATION_REQUESTED.value]:
            q.status = QuoteStatus.SUPERSEDED.value
            db.add(q)

    quote.status = QuoteStatus.APPROVED.value
    quote.approved_at = datetime.now(timezone.utc)
    if decision_in and decision_in.customer_notes:
        quote.customer_notes = decision_in.customer_notes

    # Update official repair price now that customer approved
    repair.quote_amount = quote.total_amount
    repair.quote_details = f"v{quote.version}: {quote.diagnosis} (Parts: ${quote.parts_cost}, Labor: ${quote.labor_cost}, Other: ${quote.other_fees})"
    repair.quote_approved_at = datetime.now(timezone.utc)

    db.add(quote)
    db.add(repair)
    db.commit()

    # Move repair workflow to CUSTOMER_APPROVED
    if repair.status == RepairStatus.QUOTE_PENDING.value:
        transition_repair_status(
            db=db,
            repair=repair,
            target_status=RepairStatus.CUSTOMER_APPROVED.value,
            changed_by_user_id=current_user.id,
            notes=f"Customer approved Quote v{quote.version} (${quote.total_amount:.2f}).",
            is_admin=(current_user.role == "admin"),
        )
    else:
        # Audit log for approved change request
        history = RepairHistory(
            repair_id=repair.id,
            from_status=repair.status,
            to_status=repair.status,
            changed_by_user_id=current_user.id,
            notes=f"Customer approved Change Request Quote v{quote.version} (${quote.total_amount:.2f}).",
        )
        db.add(history)
        db.commit()

    db.refresh(quote)

    # Emit notification to technician
    try:
        from app.services.notification_service import NotificationService
        from app.models.device import Device
        from app.models.technician import TechnicianProfile
        device = db.query(Device).filter(Device.id == repair.device_id).first()
        dev_label = f"{device.brand} {device.model}".strip() if device else "Device"
        if repair.technician_id:
            tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.id == repair.technician_id).first()
            if tech_prof:
                NotificationService.notify_quote_approved(
                    db=db,
                    technician_user_id=tech_prof.user_id,
                    repair_id=repair.id,
                    quote_id=quote.id,
                    total_amount=quote.total_amount,
                    device_name=dev_label
                )
    except Exception:
        pass

    return quote

@router.post("/repairs/{repair_id}/quotes/{quote_id}/reject", response_model=QuoteResponse)
def reject_quote(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_id: int,
    decision_in: Optional[QuoteDecision] = Body(default=None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Customer rejects the quote.
    If initial quote: cancels repair.
    If change request: rejects price increase.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")

    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.repair_id == repair_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    if quote.status not in [QuoteStatus.PENDING.value, QuoteStatus.CLARIFICATION_REQUESTED.value]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot reject quote with status '{quote.status}'")

    quote.status = QuoteStatus.REJECTED.value
    quote.rejected_at = datetime.now(timezone.utc)
    if decision_in and decision_in.customer_notes:
        quote.customer_notes = decision_in.customer_notes

    db.add(quote)
    db.commit()

    if quote.version == 1 and repair.status == RepairStatus.QUOTE_PENDING.value:
        transition_repair_status(
            db=db,
            repair=repair,
            target_status=RepairStatus.CANCELLED.value,
            changed_by_user_id=current_user.id,
            notes=f"Customer rejected initial Quote v1 (${quote.total_amount:.2f}) - repair cancelled.",
            is_admin=(current_user.role == "admin"),
        )
    else:
        history = RepairHistory(
            repair_id=repair.id,
            from_status=repair.status,
            to_status=repair.status,
            changed_by_user_id=current_user.id,
            notes=f"Customer rejected Change Request Quote v{quote.version} (${quote.total_amount:.2f}). Original price maintained.",
        )
        db.add(history)
        db.commit()

    db.refresh(quote)
    return quote

@router.post("/repairs/{repair_id}/quotes/{quote_id}/clarification", response_model=QuoteResponse)
def request_clarification(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_id: int,
    clarification_in: QuoteClarificationRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Customer requests clarification on a quote.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "customer" and repair.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not customer of this repair")

    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.repair_id == repair_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    quote.status = QuoteStatus.CLARIFICATION_REQUESTED.value
    quote.clarification_message = clarification_in.message
    quote.clarification_requested_at = datetime.now(timezone.utc)
    db.add(quote)
    db.commit()

    # Log audit entry
    history = RepairHistory(
        repair_id=repair.id,
        from_status=repair.status,
        to_status=repair.status,
        changed_by_user_id=current_user.id,
        notes=f"Customer requested quote clarification: '{clarification_in.message}'.",
    )
    db.add(history)
    db.commit()

    db.refresh(quote)
    return quote

@router.post("/repairs/{repair_id}/quotes/{quote_id}/clarify-response", response_model=QuoteResponse)
def respond_to_clarification(
    *,
    db: Session = Depends(get_db),
    repair_id: int,
    quote_id: int,
    response_in: QuoteClarificationResponse,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Technician responds to customer's clarification request.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")

    if current_user.role == "technician":
        tech_profile = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        if not tech_profile or repair.technician_id != tech_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned technician")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only technicians can respond to clarifications")

    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.repair_id == repair_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    quote.clarification_response = response_in.response
    quote.status = QuoteStatus.PENDING.value
    db.add(quote)
    db.commit()

    # Log audit entry
    history = RepairHistory(
        repair_id=repair.id,
        from_status=repair.status,
        to_status=repair.status,
        changed_by_user_id=current_user.id,
        notes=f"Technician answered quote clarification: '{response_in.response}'.",
    )
    db.add(history)
    db.commit()

    db.refresh(quote)
    return quote
