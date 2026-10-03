import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.payment import Payment, PaymentState
from app.models.repair import Repair
from app.models.quote import Quote
from app.models.user import User
from app.models.device import Device
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentAuthorizeRequest,
    PaymentCaptureRequest,
    PaymentRefundRequest,
    PaymentInvoiceResponse,
    InvoiceLineItem,
)
from app.services.payment.factory import get_payment_provider
from app.services.payment.base import ProviderStatus

class PaymentService:
    @staticmethod
    def generate_invoice_reference() -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m")
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"INV-{date_str}-{unique_suffix}"

    @staticmethod
    def create_intent(
        db: Session,
        current_user: User,
        intent_in: PaymentIntentCreate,
        provider_name: Optional[str] = None
    ) -> Payment:
        provider = get_payment_provider(provider_name)
        
        # 1. Resolve Amount and Order Details
        repair = None
        quote = None
        amount = intent_in.amount
        order_ref = intent_in.order_reference or f"ORD-{uuid.uuid4().hex[:6].upper()}"

        if intent_in.repair_id:
            repair = db.query(Repair).filter(Repair.id == intent_in.repair_id).first()
            if not repair:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repair not found")
            if current_user.role == "customer" and repair.customer_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted for this repair order")
            
            order_ref = f"REP-{repair.id:04d}"
            
            # If quote not explicitly passed, find latest approved quote
            if intent_in.quote_id:
                quote = db.query(Quote).filter(Quote.id == intent_in.quote_id, Quote.repair_id == repair.id).first()
            else:
                quote = db.query(Quote).filter(Quote.repair_id == repair.id, Quote.status == "APPROVED").order_by(Quote.version.desc()).first()
            
            if quote:
                amount = quote.total_amount
            elif repair.quote_amount:
                amount = repair.quote_amount
            elif amount is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No approved quote or amount found for repair")

        if amount is None or amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be greater than 0")

        # 2. Compute 15% Platform Commission and 85% Tech Payout
        fee_pct = settings.PLATFORM_FEE_PERCENTAGE / 100.0
        platform_fee = round(amount * fee_pct, 2)
        technician_payout = round(amount - platform_fee, 2)

        # 3. Call Provider to create Intent
        invoice_ref = PaymentService.generate_invoice_reference()
        result = provider.create_intent(
            amount=amount,
            currency=intent_in.currency,
            order_reference=order_ref,
            customer_email=current_user.email,
            metadata=intent_in.metadata or {}
        )

        # 4. Store Payment in DB (State: CREATED)
        payment = Payment(
            invoice_reference=invoice_ref,
            user_id=current_user.id,
            repair_id=repair.id if repair else None,
            quote_id=quote.id if quote else None,
            order_type=intent_in.order_type,
            order_reference=order_ref,
            amount=amount,
            currency=intent_in.currency.upper(),
            platform_fee=platform_fee,
            technician_payout=technician_payout,
            status=PaymentState.CREATED.value,
            provider=provider.provider_name,
            provider_transaction_id=result.provider_transaction_id,
            provider_client_token=result.client_secret,
            payment_method_type=intent_in.payment_method_type,
            metadata_json=intent_in.metadata or {}
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def authorize_payment(
        db: Session,
        payment_id: int,
        current_user: User,
        auth_in: PaymentAuthorizeRequest,
        provider_name: Optional[str] = None
    ) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
        if current_user.role == "customer" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this payment")

        if payment.status != PaymentState.CREATED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot authorize payment with status '{payment.status}'. Expected 'CREATED'."
            )

        provider = get_payment_provider(provider_name or payment.provider)
        result = provider.authorize(
            provider_transaction_id=payment.provider_transaction_id or f"tx_{payment.id}",
            amount=payment.amount,
            payment_token=auth_in.sandbox_token,
            simulate_failure=auth_in.simulate_failure,
            failure_reason=auth_in.failure_reason
        )

        now = datetime.now(timezone.utc)
        if result.success and result.status == ProviderStatus.AUTHORIZED:
            payment.status = PaymentState.AUTHORIZED.value
            payment.authorized_at = now
            payment.card_brand = result.card_brand or "Visa"
            payment.card_last4 = result.card_last4 or "4242"
            payment.failure_reason = None
        else:
            payment.status = PaymentState.FAILED.value
            payment.failure_reason = result.failure_reason or "Payment authorization failed"

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def capture_payment(
        db: Session,
        payment_id: int,
        current_user: User,
        capture_in: Optional[PaymentCaptureRequest] = None,
        provider_name: Optional[str] = None
    ) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
        if current_user.role == "customer" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this payment")

        if payment.status != PaymentState.AUTHORIZED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot capture payment with status '{payment.status}'. Expected 'AUTHORIZED'."
            )

        amount_to_capture = capture_in.amount_to_capture if capture_in and capture_in.amount_to_capture else payment.amount
        provider = get_payment_provider(provider_name or payment.provider)
        result = provider.capture(
            provider_transaction_id=payment.provider_transaction_id or f"tx_{payment.id}",
            amount=amount_to_capture
        )

        now = datetime.now(timezone.utc)
        if result.success and result.status == ProviderStatus.CAPTURED:
            payment.status = PaymentState.CAPTURED.value
            payment.captured_at = now
            
            # If linked to a repair, record paid status
            if payment.repair_id:
                repair = db.query(Repair).filter(Repair.id == payment.repair_id).first()
                if repair:
                    repair.quote_amount = payment.amount
                    db.add(repair)
        else:
            payment.status = PaymentState.FAILED.value
            payment.failure_reason = result.failure_reason or "Payment capture failed"

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def process_complete_checkout(
        db: Session,
        current_user: User,
        intent_in: PaymentIntentCreate,
        provider_name: Optional[str] = None
    ) -> Payment:
        """
        One-step end-to-end checkout helper (CREATE -> AUTHORIZE -> CAPTURE).
        Ideal for single-page checkout and mobile instant payments.
        """
        payment = PaymentService.create_intent(db, current_user, intent_in, provider_name)
        
        # Authorize
        auth_req = PaymentAuthorizeRequest(
            sandbox_token=intent_in.sandbox_token or "tok_sandbox_success",
            simulate_failure=(intent_in.sandbox_token in ["tok_sandbox_decline", "tok_chargeDeclined"])
        )
        payment = PaymentService.authorize_payment(db, payment.id, current_user, auth_req, provider_name)
        
        # Capture if authorized
        if payment.status == PaymentState.AUTHORIZED.value:
            payment = PaymentService.capture_payment(db, payment.id, current_user, None, provider_name)
        
        return payment

    @staticmethod
    def refund_payment(
        db: Session,
        payment_id: int,
        current_user: User,
        refund_in: PaymentRefundRequest,
        provider_name: Optional[str] = None
    ) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        if current_user.role != "admin" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required to refund payments")

        if payment.status != PaymentState.CAPTURED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot refund payment with status '{payment.status}'. Expected 'CAPTURED'."
            )

        refund_amt = refund_in.refund_amount or payment.amount
        provider = get_payment_provider(provider_name or payment.provider)
        result = provider.refund(
            provider_transaction_id=payment.provider_transaction_id or f"tx_{payment.id}",
            amount=refund_amt,
            reason=refund_in.reason
        )

        now = datetime.now(timezone.utc)
        if result.success and result.status == ProviderStatus.REFUNDED:
            payment.status = PaymentState.REFUNDED.value
            payment.refunded_at = now
            payment.refund_reason = refund_in.reason
            payment.refunded_amount = refund_amt
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=result.failure_reason or "Provider rejected refund operation"
            )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def get_invoice_details(
        db: Session,
        payment_id: int,
        current_user: User
    ) -> PaymentInvoiceResponse:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
        if current_user.role == "customer" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this invoice")

        user = db.query(User).filter(User.id == payment.user_id).first()
        device_label = None
        line_items: List[InvoiceLineItem] = []

        if payment.quote_id:
            quote = db.query(Quote).filter(Quote.id == payment.quote_id).first()
            if quote:
                if quote.labor_cost > 0:
                    line_items.append(InvoiceLineItem(description="Technician Labor & Diagnostic Rework", amount=quote.labor_cost))
                if quote.parts_cost > 0:
                    line_items.append(InvoiceLineItem(description="Replacement Hardware & Modules", amount=quote.parts_cost))
                if quote.other_fees > 0:
                    line_items.append(InvoiceLineItem(description="Platform Logistics & Environmental Disposal", amount=quote.other_fees))

        if payment.repair_id:
            repair = db.query(Repair).filter(Repair.id == payment.repair_id).first()
            if repair and repair.device_id:
                dev = db.query(Device).filter(Device.id == repair.device_id).first()
                if dev:
                    device_label = f"{dev.brand} {dev.model}"

        if not line_items:
            line_items.append(InvoiceLineItem(description=f"{payment.order_type} Service Order ({payment.order_reference})", amount=payment.amount))

        payment_method_display = "Credit / Debit Card"
        if payment.card_brand and payment.card_last4:
            payment_method_display = f"{payment.card_brand} •••• {payment.card_last4}"

        return PaymentInvoiceResponse(
            invoice_reference=payment.invoice_reference,
            payment_id=payment.id,
            status=PaymentState(payment.status),
            customer_name=user.name if user and user.name else (user.email if user else "Customer"),
            customer_email=user.email if user else "",
            order_reference=payment.order_reference,
            order_type=payment.order_type,
            device_model=device_label,
            currency=payment.currency,
            subtotal=payment.amount - payment.platform_fee,
            platform_fee=payment.platform_fee,
            total_amount=payment.amount,
            payment_method_display=payment_method_display,
            transaction_reference=payment.provider_transaction_id or payment.invoice_reference,
            provider=payment.provider,
            is_sandbox=True,
            paid_at=payment.captured_at or payment.authorized_at,
            line_items=line_items
        )
