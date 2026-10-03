from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.payment import Payment, PaymentState
from app.models.repair import Repair
from app.models.technician import TechnicianProfile
from app.models.user import User
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentAuthorizeRequest,
    PaymentCaptureRequest,
    PaymentRefundRequest,
    PaymentResponse,
    PaymentInvoiceResponse,
    PaymentListResponse,
)
from app.services.payment_service import PaymentService
from app.core.rate_limit import payment_rate_limiter
from app.api import deps

router = APIRouter()

@router.post("/create-intent", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_intent(
    request: Request,
    *,
    db: Session = Depends(get_db),
    intent_in: PaymentIntentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Creates a new Payment Intent in CREATED state.
    Calculates 15% platform fee and sets up provider transaction reference.
    """
    payment_rate_limiter.check_rate_limit(request)
    return PaymentService.create_intent(db=db, current_user=current_user, intent_in=intent_in)

@router.post("/{payment_id}/authorize", response_model=PaymentResponse)
def authorize_payment(
    payment_id: int,
    *,
    db: Session = Depends(get_db),
    auth_in: PaymentAuthorizeRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Authorizes a CREATED payment. Transitions state to AUTHORIZED or FAILED.
    """
    return PaymentService.authorize_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user,
        auth_in=auth_in
    )

@router.post("/{payment_id}/capture", response_model=PaymentResponse)
def capture_payment(
    payment_id: int,
    *,
    db: Session = Depends(get_db),
    capture_in: Optional[PaymentCaptureRequest] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Settles an AUTHORIZED payment. Transitions state to CAPTURED.
    """
    return PaymentService.capture_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user,
        capture_in=capture_in
    )

@router.post("/checkout", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def process_instant_checkout(
    request: Request,
    *,
    db: Session = Depends(get_db),
    checkout_in: PaymentIntentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    One-step direct checkout (CREATED -> AUTHORIZED -> CAPTURED) for mobile and web apps.
    """
    payment_rate_limiter.check_rate_limit(request)
    return PaymentService.process_complete_checkout(
        db=db,
        current_user=current_user,
        intent_in=checkout_in
    )

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    *,
    db: Session = Depends(get_db),
    refund_in: PaymentRefundRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Refunds a CAPTURED payment. Transitions state to REFUNDED.
    """
    return PaymentService.refund_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user,
        refund_in=refund_in
    )

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get payment status and details by ID with strict role isolation.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    if current_user.role == "customer":
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role == "technician":
        tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_prof.id if tech_prof else -1
        is_assigned_repair = False
        if payment.repair_id:
            rep = db.query(Repair).filter(Repair.id == payment.repair_id, Repair.technician_id == tech_id).first()
            if rep:
                is_assigned_repair = True
        if not is_assigned_repair:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Technicians can only access payments for assigned repairs")
    elif current_user.role != "admin":
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return payment

@router.get("/{payment_id}/invoice", response_model=PaymentInvoiceResponse)
def get_customer_invoice(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Customer invoice view displaying:
    - Amount
    - Order Reference
    - Payment Status (CREATED, AUTHORIZED, CAPTURED, FAILED, REFUNDED)
    - Invoice / Transaction Reference
    """
    return PaymentService.get_invoice_details(db=db, payment_id=payment_id, current_user=current_user)

@router.get("/repair/{repair_id}", response_model=Optional[PaymentResponse])
def get_repair_payment(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get latest payment record associated with a repair order.
    """
    payment = db.query(Payment).filter(Payment.repair_id == repair_id).order_by(Payment.created_at.desc()).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payment found for this repair")
    
    if current_user.role == "customer":
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role == "technician":
        tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_prof.id if tech_prof else -1
        rep = db.query(Repair).filter(Repair.id == repair_id, Repair.technician_id == tech_id).first()
        if not rep:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Technicians can only access payments for assigned repairs")
    elif current_user.role != "admin":
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return payment

@router.get("", response_model=PaymentListResponse)
def list_payments(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List payments with role-based access:
      - Customers see only their own payments.
      - Technicians see only payments related to repairs assigned to them.
      - Admins see all payments.
    """
    query = db.query(Payment)
    if current_user.role == "customer":
        query = query.filter(Payment.user_id == current_user.id)
    elif current_user.role == "technician":
        tech_prof = db.query(TechnicianProfile).filter(TechnicianProfile.user_id == current_user.id).first()
        tech_id = tech_prof.id if tech_prof else -1
        assigned_repair_ids = [
            r.id for r in db.query(Repair.id).filter(Repair.technician_id == tech_id).all()
        ]
        query = query.filter(Payment.repair_id.in_(assigned_repair_ids))

    if status_filter:
        query = query.filter(Payment.status == status_filter.upper())

    total = query.count()
    items = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}
