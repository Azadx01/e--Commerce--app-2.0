from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class TechnicianProfile(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    years_of_experience = Column(Integer, nullable=True, default=1)
    profile_picture_url = Column(String(500), nullable=True)
    skills = Column(JSON, nullable=False, default=list)  # e.g. ["Screen Replacement", "Battery Replacement", "Micro-soldering"]
    device_categories = Column(JSON, nullable=False, default=list)  # e.g. ["smartphone", "laptop"]
    service_area = Column(String(255), nullable=False, default="Metro Area")
    service_radius_km = Column(Float, nullable=True, default=25.0)
    verification_status = Column(String(50), nullable=False, default="pending")  # pending, verified, rejected
    rating = Column(Float, nullable=False, default=5.0)
    total_reviews = Column(Integer, nullable=False, default=0)
    availability = Column(String(50), nullable=False, default="available")  # available, busy, offline
    is_available = Column(Boolean, nullable=False, default=True)
    hourly_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="technician_profile")
    repairs = relationship("Repair", back_populates="technician")

    @property
    def name(self) -> str:
        if self.user and self.user.name:
            return self.user.name
        return self.business_name or f"Technician #{self.id}"

    @property
    def email(self) -> str:
        if self.user:
            return self.user.email
        return ""
