# routers/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, Notification, User
from core.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    
    # FR-64: Calculate unread count
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at == None
    ).count()
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(404, "Bildirim bulunamadı")
    if notification.user_id != current_user.id:
        raise HTTPException(403, "Bu bildirimi okuma yetkiniz yok")
    
    notification.read_at = datetime.utcnow()
    db.commit()
    return {"message": "Bildirim okundu olarak işaretlendi"}


@router.patch("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at == None
    ).update({"read_at": datetime.utcnow()})
    db.commit()
    return {"message": "Tüm bildirimler okundu olarak işaretlendi"}
