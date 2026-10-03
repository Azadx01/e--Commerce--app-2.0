import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.services.payment.base import (
    BasePaymentProvider,
    PaymentResult,
    PaymentRefundResult,
    ProviderStatus,
)

class SandboxPaymentProvider(BasePaymentProvider):
    """
    Dedicated Development & Testing Sandbox Payment Provider.
    Implements deterministic card simulation, zero live credentials required,
    and simulated edge-case responses for development and unit testing.
    """

    @property
    def provider_name(self) -> str:
        return "sandbox"

    @property
    def is_sandbox(self) -> bool:
        return True

    def create_intent(
        self,
        amount: float,
        currency: str,
        order_reference: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        tx_id = f"sbx_pi_{uuid.uuid4().hex[:12]}"
        client_secret = f"{tx_id}_secret_{uuid.uuid4().hex[:16]}"
        return PaymentResult(
            success=True,
            status=ProviderStatus.REQUIRES_ACTION,
            provider_transaction_id=tx_id,
            client_secret=client_secret,
            payment_method_type="card",
            raw_response={
                "provider": "sandbox",
                "mode": "test",
                "amount": amount,
                "currency": currency,
                "order_reference": order_reference,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def authorize(
        self,
        provider_transaction_id: str,
        amount: float,
        payment_token: Optional[str] = "tok_sandbox_success",
        simulate_failure: bool = False,
        failure_reason: Optional[str] = None
    ) -> PaymentResult:
        token = (payment_token or "tok_sandbox_success").lower()

        # Deterministic simulation triggers
        if simulate_failure or token in ["tok_sandbox_decline", "tok_decline"]:
            return PaymentResult(
                success=False,
                status=ProviderStatus.FAILED,
                provider_transaction_id=provider_transaction_id,
                failure_reason=failure_reason or "Card was declined by issuing bank (Sandbox simulation)",
                raw_response={"code": "card_declined", "token": token}
            )
        elif token in ["tok_insufficient_funds", "tok_sandbox_insufficient"]:
            return PaymentResult(
                success=False,
                status=ProviderStatus.FAILED,
                provider_transaction_id=provider_transaction_id,
                failure_reason="Insufficient balance on card account (Sandbox simulation)",
                raw_response={"code": "insufficient_funds", "token": token}
            )
        elif token in ["tok_fraud_risk", "tok_sandbox_fraud"]:
            return PaymentResult(
                success=False,
                status=ProviderStatus.FAILED,
                provider_transaction_id=provider_transaction_id,
                failure_reason="Transaction blocked by automated risk filter (Sandbox simulation)",
                raw_response={"code": "high_risk_fraud", "token": token}
            )

        # Successful authorization simulation
        brand = "Visa"
        last4 = "4242"
        if "mastercard" in token:
            brand = "Mastercard"
            last4 = "5555"
        elif "amex" in token:
            brand = "American Express"
            last4 = "3782"
        elif "apple" in token:
            brand = "Apple Pay"
            last4 = "8812"

        return PaymentResult(
            success=True,
            status=ProviderStatus.AUTHORIZED,
            provider_transaction_id=provider_transaction_id,
            payment_method_type="card",
            card_brand=brand,
            card_last4=last4,
            raw_response={
                "auth_code": f"AUTH_{uuid.uuid4().hex[:6].upper()}",
                "authorized_amount": amount,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def capture(
        self,
        provider_transaction_id: str,
        amount: float
    ) -> PaymentResult:
        return PaymentResult(
            success=True,
            status=ProviderStatus.CAPTURED,
            provider_transaction_id=provider_transaction_id,
            raw_response={
                "capture_id": f"sbx_cap_{uuid.uuid4().hex[:12]}",
                "captured_amount": amount,
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "settlement_status": "settled",
            }
        )

    def refund(
        self,
        provider_transaction_id: str,
        amount: float,
        reason: str
    ) -> PaymentRefundResult:
        refund_id = f"sbx_rf_{uuid.uuid4().hex[:12]}"
        return PaymentRefundResult(
            success=True,
            refund_transaction_id=refund_id,
            refunded_amount=amount,
            status=ProviderStatus.REFUNDED,
            raw_response={
                "refund_id": refund_id,
                "original_txn": provider_transaction_id,
                "amount": amount,
                "reason": reason,
                "refunded_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_status(
        self,
        provider_transaction_id: str
    ) -> PaymentResult:
        return PaymentResult(
            success=True,
            status=ProviderStatus.CAPTURED,
            provider_transaction_id=provider_transaction_id,
            card_brand="Visa",
            card_last4="4242"
        )
