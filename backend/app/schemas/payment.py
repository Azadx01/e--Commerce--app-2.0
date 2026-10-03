from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

class PaymentState(str, Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentIntentCreate(BaseModel):
    repair_id: Optional[int] = None
    quote_id: Optional[int] = None
    order_type: str = "REPAIR"
    order_reference: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    payment_method_type: str = "card"
    # Test card / sandbox token for test/sandbox mode (e.g. "tok_sandbox_success", "tok_sandbox_decline")
    sandbox_token: Optional[str] = "tok_sandbox_success"
    metadata: Optional[Dict[str, Any]] = None

class PaymentAuthorizeRequest(BaseModel):
    sandbox_token: Optional[str] = "tok_sandbox_success"
    simulate_failure: bool = False
    failure_reason: Optional[str] = None

class PaymentCaptureRequest(BaseModel):
    amount_to_capture: Optional[float] = None

class PaymentRefundRequest(BaseModel):
    refund_amount: Optional[float] = None
    reason: str = "Customer requested cancellation or dispute resolution"

class PaymentResponse(BaseModel):
    id: int
    invoice_reference: str
    user_id: int
    repair_id: Optional[int] = None
    quote_id: Optional[int] = None
    order_type: str
    order_reference: str
    amount: float
    currency: str
    platform_fee: float
    technician_payout: float
    status: PaymentState
    provider: str
    provider_transaction_id: Optional[str] = None
    provider_client_token: Optional[str] = None
    payment_method_type: Optional[str] = None
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    failure_reason: Optional[str] = None
    refund_reason: Optional[str] = None
    refunded_amount: Optional[float] = 0.0
    created_at: datetime
    authorized_at: Optional[datetime] = None
    captured_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceLineItem(BaseModel):
    description: str
    amount: float

class PaymentInvoiceResponse(BaseModel):
    invoice_reference: str
    payment_id: int
    status: PaymentState
    customer_name: str
    customer_email: str
    order_reference: str
    order_type: str
    device_model: Optional[str] = None
    currency: str
    subtotal: float
    platform_fee: float
    total_amount: float
    payment_method_display: str
    transaction_reference: Optional[str] = None
    provider: str
    is_sandbox: bool
    paid_at: Optional[datetime] = None
    line_items: List[InvoiceLineItem] = []

class PaymentListResponse(BaseModel):
    total: int
    items: List[PaymentResponse]
