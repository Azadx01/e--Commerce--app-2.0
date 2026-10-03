from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    NotificationTriggerRequest,
    NotificationEventType
)
from app.services.notification_service import NotificationService
from app.api import deps

router = APIRouter()

@router.get("", response_model=NotificationListResponse)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_read: Optional[bool] = Query(None),
    event_type: Optional[str] = Query(None)
) -> Any:
    """
    Retrieve paginated notifications for the current authenticated user.
    """
    items = NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_read=is_read,
        event_type=event_type
    )
    unread_count = NotificationService.get_unread_count(db=db, user_id=current_user.id)
    return {
        "total": len(items),
        "unread_count": unread_count,
        "items": items
    }

@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the count of unread notifications for badge counter.
    """
    count = NotificationService.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a specific notification as read.
    """
    notification = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

@router.post("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark all unread notifications for the current user as read.
    """
    updated = NotificationService.mark_all_as_read(db=db, user_id=current_user.id)
    return {"message": "All notifications marked as read", "updated_count": updated}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> None:
    """
    Delete a notification.
    """
    success = NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

@router.post("/test-event", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def trigger_test_notification_event(
    payload: NotificationTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Trigger one of the 10 lifecycle events for testing in-app notifications.
    """
    event = payload.event_type
    dev = payload.device_name or "iPhone 14 Pro"
    tech = payload.technician_name or "Apex Precision Repairs"
    amt = payload.amount or 185.0
    eid = payload.entity_id or 1

    if event == NotificationEventType.REPAIR_REQUEST_CREATED:
        return NotificationService.notify_repair_request_created(db, current_user.id, eid, dev)
    elif event == NotificationEventType.TECHNICIAN_ACCEPTED:
        return NotificationService.notify_technician_accepted(db, current_user.id, eid, tech, dev)
    elif event == NotificationEventType.QUOTE_RECEIVED:
        return NotificationService.notify_quote_received(db, current_user.id, eid, 101, amt, dev)
    elif event == NotificationEventType.QUOTE_APPROVED:
        return NotificationService.notify_quote_approved(db, current_user.id, eid, 101, amt, dev)
    elif event == NotificationEventType.REPAIR_STARTED:
        return NotificationService.notify_repair_started(db, current_user.id, eid, dev, tech)
    elif event == NotificationEventType.PARTS_REQUIRED:
        return NotificationService.notify_parts_required(db, current_user.id, eid, payload.part_name or "OLED Panel", dev)
    elif event == NotificationEventType.REPAIR_COMPLETED:
        return NotificationService.notify_repair_completed(db, current_user.id, eid, dev)
    elif event == NotificationEventType.WARRANTY_STARTED:
        return NotificationService.notify_warranty_started(db, current_user.id, dev, "180 days", "2027-03-30")
    elif event == NotificationEventType.RESALE_QUOTE_AVAILABLE:
        return NotificationService.notify_resale_quote_available(db, current_user.id, dev, amt, eid)
    elif event == NotificationEventType.RESALE_STATUS_CHANGED:
        return NotificationService.notify_resale_status_changed(db, current_user.id, dev, payload.status_text or "OFFER_ACCEPTED", eid)
    else:
        return NotificationService.create_notification(
            db, current_user.id, event, "Notification Alert", f"Event triggered for {dev}", "system", eid
        )
