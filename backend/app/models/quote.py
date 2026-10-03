from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True, index=True)
    
    version = Column(Integer, nullable=False, default=1)
    is_change_request = Column(Boolean, nullable=False, default=False)
    
    diagnosis = Column(Text, nullable=False)
    labor_cost = Column(Float, nullable=False, default=0.0)
    parts_cost = Column(Float, nullable=False, default=0.0)
    other_fees = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    
    expected_completion_time = Column(String(100), nullable=False)
    warranty_duration = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    before_repair_images = Column(JSON, nullable=True, default=list)
    
    # Status: PENDING, APPROVED, REJECTED, CLARIFICATION_REQUESTED, SUPERSEDED
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    
    customer_notes = Column(Text, nullable=True)
    clarification_message = Column(Text, nullable=True)
    clarification_response = Column(Text, nullable=True)
    clarification_requested_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    repair = relationship("Repair", back_populates="quotes")
    technician = relationship("TechnicianProfile")
    payments = relationship("Payment", back_populates="quote", cascade="all, delete-orphan", order_by="Payment.created_at.desc()")
