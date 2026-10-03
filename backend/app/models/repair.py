from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Repair(Base):
    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id", ondelete="SET NULL"), nullable=True, index=True)
    
    status = Column(String(50), nullable=False, default="REQUESTED", index=True)
    problem_description = Column(Text, nullable=False)
    customer_notes = Column(Text, nullable=True)
    inspection_notes = Column(Text, nullable=True)
    quote_amount = Column(Float, nullable=True)
    quote_details = Column(Text, nullable=True)
    quote_approved_at = Column(DateTime(timezone=True), nullable=True)
    quote_rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("User", foreign_keys=[customer_id], back_populates="repairs")
    device = relationship("Device", back_populates="repairs")
    technician = relationship("TechnicianProfile", back_populates="repairs")
    diagnostic = relationship("Diagnostic")
    status_history = relationship(
        "RepairHistory",
        back_populates="repair",
        cascade="all, delete-orphan",
        order_by="RepairHistory.created_at.asc()"
    )
    quotes = relationship(
        "Quote",
        back_populates="repair",
        cascade="all, delete-orphan",
        order_by="Quote.version.asc()"
    )
    payments = relationship("Payment", back_populates="repair", cascade="all, delete-orphan", order_by="Payment.created_at.desc()")

class RepairHistory(Base):
    __tablename__ = "repair_status_history"

    id = Column(Integer, primary_key=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    changed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    repair = relationship("Repair", back_populates="status_history")
    changed_by = relationship("User")
