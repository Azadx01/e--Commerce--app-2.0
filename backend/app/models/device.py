from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number_hash = Column(String(255), nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    condition = Column(String(100), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="devices")
    images = relationship("DeviceImage", back_populates="device", cascade="all, delete-orphan")
    diagnostics = relationship("Diagnostic", back_populates="device", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="device", cascade="all, delete-orphan")
    repairs = relationship("Repair", back_populates="device", cascade="all, delete-orphan")

class DeviceImage(Base):
    __tablename__ = "device_images"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    storage_url = Column(String(500), nullable=False)
    image_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device", back_populates="images")
