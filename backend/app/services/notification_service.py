from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notification import Notification
from app.schemas.notification import NotificationEventType

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        event_type: NotificationEventType | str,
        title: str,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> Notification:
        event_str = event_type.value if isinstance(event_type, NotificationEventType) else str(event_type)
        notification = Notification(
            user_id=user_id,
            event_type=event_str,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json or {},
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    # --- 10 Specified Domain Event Handlers ---

    @staticmethod
    def notify_repair_request_created(
        db: Session,
        user_id: int,
        repair_id: int,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.REPAIR_REQUEST_CREATED,
            title="Repair Request Created",
            message=f"Your repair request for {device_name} has been received and broadcast to qualified technicians.",
            entity_type="repair",
            entity_id=repair_id,
            metadata_json={"repair_id": repair_id, "device_name": device_name}
        )

    @staticmethod
    def notify_technician_accepted(
        db: Session,
        user_id: int,
        repair_id: int,
        technician_name: str,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.TECHNICIAN_ACCEPTED,
            title="Technician Assigned",
            message=f"{technician_name} has accepted your repair request for {device_name}.",
            entity_type="repair",
            entity_id=repair_id,
            metadata_json={"repair_id": repair_id, "technician_name": technician_name, "device_name": device_name}
        )

    @staticmethod
    def notify_quote_received(
        db: Session,
        user_id: int,
        repair_id: int,
        quote_id: int,
        total_amount: float,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.QUOTE_RECEIVED,
            title="New Repair Quote Ready",
            message=f"An itemized quote of ${total_amount:.2f} is ready for your {device_name}. Review and approve to proceed.",
            entity_type="quote",
            entity_id=quote_id,
            metadata_json={"repair_id": repair_id, "quote_id": quote_id, "amount": total_amount, "device_name": device_name}
        )

    @staticmethod
    def notify_quote_approved(
        db: Session,
        technician_user_id: int,
        repair_id: int,
        quote_id: int,
        total_amount: float,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=technician_user_id,
            event_type=NotificationEventType.QUOTE_APPROVED,
            title="Quote Approved by Customer",
            message=f"The customer approved quote #{quote_id} (${total_amount:.2f}) for {device_name}. You may begin work.",
            entity_type="quote",
            entity_id=quote_id,
            metadata_json={"repair_id": repair_id, "quote_id": quote_id, "amount": total_amount, "device_name": device_name}
        )

    @staticmethod
    def notify_repair_started(
        db: Session,
        user_id: int,
        repair_id: int,
        device_name: str,
        technician_name: Optional[str] = None
    ) -> Notification:
        tech_str = f" by {technician_name}" if technician_name else ""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.REPAIR_STARTED,
            title="Repair Started",
            message=f"Diagnostic inspection passed. Repair has commenced on your {device_name}{tech_str}.",
            entity_type="repair",
            entity_id=repair_id,
            metadata_json={"repair_id": repair_id, "device_name": device_name}
        )

    @staticmethod
    def notify_parts_required(
        db: Session,
        user_id: int,
        repair_id: int,
        part_name: str,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.PARTS_REQUIRED,
            title="Replacement Parts Ordered",
            message=f"Genuine replacement part '{part_name}' has been allocated from central supply for your {device_name}.",
            entity_type="repair",
            entity_id=repair_id,
            metadata_json={"repair_id": repair_id, "part_name": part_name, "device_name": device_name}
        )

    @staticmethod
    def notify_repair_completed(
        db: Session,
        user_id: int,
        repair_id: int,
        device_name: str
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.REPAIR_COMPLETED,
            title="Repair Completed & QA Passed",
            message=f"Your {device_name} has successfully cleared all quality assurance checks and is ready for pickup or delivery.",
            entity_type="repair",
            entity_id=repair_id,
            metadata_json={"repair_id": repair_id, "device_name": device_name}
        )

    @staticmethod
    def notify_warranty_started(
        db: Session,
        user_id: int,
        device_name: str,
        duration_text: str = "180 days",
        expiry_date: Optional[str] = None
    ) -> Notification:
        exp_str = f" through {expiry_date}" if expiry_date else ""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.WARRANTY_STARTED,
            title="Warranty Protection Activated",
            message=f"Your {duration_text} warranty coverage for {device_name} is now active{exp_str}. Certificate anchored in Device Passport.",
            entity_type="warranty",
            metadata_json={"device_name": device_name, "duration": duration_text, "expiry_date": expiry_date}
        )

    @staticmethod
    def notify_resale_quote_available(
        db: Session,
        user_id: int,
        device_name: str,
        valuation_amount: float,
        resale_id: Optional[int] = None
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.RESALE_QUOTE_AVAILABLE,
            title="Resale Valuation Ready",
            message=f"Your AI trade-in offer of ${valuation_amount:.2f} for {device_name} is available. Lock in your quote now.",
            entity_type="resale",
            entity_id=resale_id,
            metadata_json={"device_name": device_name, "valuation": valuation_amount, "resale_id": resale_id}
        )

    @staticmethod
    def notify_resale_status_changed(
        db: Session,
        user_id: int,
        device_name: str,
        new_status: str,
        resale_id: Optional[int] = None
    ) -> Notification:
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            event_type=NotificationEventType.RESALE_STATUS_CHANGED,
            title="Resale Status Updated",
            message=f"The status of your trade-in request for {device_name} was updated to: {new_status}.",
            entity_type="resale",
            entity_id=resale_id,
            metadata_json={"device_name": device_name, "status": new_status, "resale_id": resale_id}
        )

    # --- Query & Management ---

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        is_read: Optional[bool] = None,
        event_type: Optional[str] = None
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        if event_type:
            query = query.filter(Notification.event_type == event_type)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        updated_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update(
            {"is_read": True, "read_at": now},
            synchronize_session=False
        )
        db.commit()
        return updated_count

    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notification:
            db.delete(notification)
            db.commit()
            return True
        return False
