from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="customer") # customer, technician, admin
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    technician_profile = relationship("TechnicianProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    repairs = relationship("Repair", foreign_keys="Repair.customer_id", back_populates="customer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan", order_by="Notification.created_at.desc()")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan", order_by="Payment.created_at.desc()")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
