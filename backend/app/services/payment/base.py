from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ProviderStatus(str, Enum):
    REQUIRES_ACTION = "REQUIRES_ACTION"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class PaymentResult:
    success: bool
    status: ProviderStatus
    provider_transaction_id: str
    client_secret: Optional[str] = None
    payment_method_type: str = "card"
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    failure_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

@dataclass
class PaymentRefundResult:
    success: bool
    refund_transaction_id: str
    refunded_amount: float
    status: ProviderStatus
    failure_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class BasePaymentProvider(ABC):
    """
    Abstract Payment Provider Interface.
    Enables swapping out providers (Sandbox, Stripe, Razorpay, Adyen) without altering business logic.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier of the payment provider."""
        pass

    @property
    @abstractmethod
    def is_sandbox(self) -> bool:
        """True if operating in test/sandbox development environment."""
        pass

    @abstractmethod
    def create_intent(
        self,
        amount: float,
        currency: str,
        order_reference: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """Initiates a payment intent or transaction draft on the provider."""
        pass

    @abstractmethod
    def authorize(
        self,
        provider_transaction_id: str,
        amount: float,
        payment_token: Optional[str] = None,
        simulate_failure: bool = False,
        failure_reason: Optional[str] = None
    ) -> PaymentResult:
        """Reserves funds on customer card/payment instrument."""
        pass

    @abstractmethod
    def capture(
        self,
        provider_transaction_id: str,
        amount: float
    ) -> PaymentResult:
        """Settles authorized funds from customer account into merchant account."""
        pass

    @abstractmethod
    def refund(
        self,
        provider_transaction_id: str,
        amount: float,
        reason: str
    ) -> PaymentRefundResult:
        """Disburses full or partial refund back to customer original payment method."""
        pass

    @abstractmethod
    def get_status(
        self,
        provider_transaction_id: str
    ) -> PaymentResult:
        """Queries provider for real-time transaction state."""
        pass
