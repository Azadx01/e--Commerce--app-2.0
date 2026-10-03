from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    device_age = Column(Float, nullable=False)
    device_condition = Column(String(50), nullable=False)
    repair_estimate = Column(Float, nullable=False)
    current_estimated_resale_value = Column(Float, nullable=False)
    new_device_reference_price = Column(Float, nullable=False)
    warranty_status = Column(String(50), nullable=False)
    user_priority = Column(String(50), nullable=True, default="balanced")
    
    # Calculated metrics
    repair_ratio = Column(Float, nullable=False)
    repair_vs_new = Column(Float, nullable=False)
    estimated_value_after_repair = Column(Float, nullable=False)
    
    # Options and analysis
    result_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("Device", back_populates="decisions")
