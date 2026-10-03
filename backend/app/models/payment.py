from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class PaymentState(str, enum.Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_reference = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id", ondelete="SET NULL"), nullable=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="SET NULL"), nullable=True, index=True)

    order_type = Column(String(50), default="REPAIR", nullable=False)
    order_reference = Column(String(100), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    platform_fee = Column(Float, default=0.0, nullable=False)
    technician_payout = Column(Float, default=0.0, nullable=False)

    status = Column(String(30), default=PaymentState.CREATED.value, nullable=False, index=True)
    provider = Column(String(50), default="sandbox", nullable=False)
    provider_transaction_id = Column(String(255), index=True, nullable=True)
    provider_client_token = Column(String(500), nullable=True)

    # Strictly NO Card Number, CVV, or Expiry stored in database (PCI-DSS compliance)
    payment_method_type = Column(String(50), default="card", nullable=True)
    card_brand = Column(String(50), nullable=True) # e.g. "Visa", "Mastercard"
    card_last4 = Column(String(4), nullable=True)  # e.g. "4242" (masked presentation only)

    failure_reason = Column(Text, nullable=True)
    refund_reason = Column(Text, nullable=True)
    refunded_amount = Column(Float, default=0.0, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    authorized_at = Column(DateTime(timezone=True), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="payments")
    repair = relationship("Repair", back_populates="payments")
    quote = relationship("Quote", back_populates="payments")
