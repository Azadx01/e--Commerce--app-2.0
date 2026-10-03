from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

class NotificationEventType(str, Enum):
    REPAIR_REQUEST_CREATED = "REPAIR_REQUEST_CREATED"
    TECHNICIAN_ACCEPTED = "TECHNICIAN_ACCEPTED"
    QUOTE_RECEIVED = "QUOTE_RECEIVED"
    QUOTE_APPROVED = "QUOTE_APPROVED"
    REPAIR_STARTED = "REPAIR_STARTED"
    PARTS_REQUIRED = "PARTS_REQUIRED"
    REPAIR_COMPLETED = "REPAIR_COMPLETED"
    WARRANTY_STARTED = "WARRANTY_STARTED"
    RESALE_QUOTE_AVAILABLE = "RESALE_QUOTE_AVAILABLE"
    RESALE_STATUS_CHANGED = "RESALE_STATUS_CHANGED"

class NotificationBase(BaseModel):
    event_type: NotificationEventType
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationResponse]

class UnreadCountResponse(BaseModel):
    unread_count: int

class NotificationTriggerRequest(BaseModel):
    event_type: NotificationEventType
    entity_id: Optional[int] = None
    device_name: Optional[str] = "iPhone 14 Pro"
    technician_name: Optional[str] = "Bob's Micro Repairs"
    amount: Optional[float] = 185.0
    status_text: Optional[str] = "APPROVED"
    part_name: Optional[str] = "OEM OLED Display"
