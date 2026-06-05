# routers/messages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from database import get_db, Message, User
from core.auth import get_current_user  # Changed from require_verified
from utils.timezone import to_iso_turkish

# Try to import notification service, but don't fail if it doesn't exist
try:
    from services.notification_service import create_notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    print("Warning: Notification service not available")

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get unique conversation partners
        sent = db.query(Message.receiver_id).filter(Message.sender_id == current_user.id).distinct()
        received = db.query(Message.sender_id).filter(Message.receiver_id == current_user.id).distinct()
        
        partner_ids = set([r[0] for r in sent] + [r[0] for r in received])
        
        # If no conversations, return empty list
        if not partner_ids:
            return {"conversations": []}
        
        partners = db.query(User).filter(User.id.in_(partner_ids)).all()
        
        conversations = []
        for p in partners:
            try:
                # Get last message with this partner
                last_msg = (
                    db.query(Message)
                    .filter(
                        or_(
                            and_(Message.sender_id == current_user.id, Message.receiver_id == p.id),
                            and_(Message.sender_id == p.id, Message.receiver_id == current_user.id)
                        )
                    )
                    .order_by(Message.created_at.desc())
                    .first()
                )
                
                # Count unread messages from this partner
                unread_count = (
                    db.query(Message)
                    .filter(
                        Message.sender_id == p.id,
                        Message.receiver_id == current_user.id,
                        Message.read_at == None
                    )
                    .count()
                )
                
                # Get profile photo (safely handle missing profile)
                photo_url = None
                try:
                    if hasattr(p, 'profile') and p.profile and hasattr(p.profile, 'photo_url'):
                        photo_url = p.profile.photo_url
                except Exception:
                    photo_url = None
                
                # Get last message preview
                last_message_preview = None
                if last_msg:
                    if last_msg.content:
                        last_message_preview = last_msg.content[:50]
                    elif hasattr(last_msg, 'message_type'):
                        if last_msg.message_type == "IMAGE":
                            last_message_preview = "📷 Fotoğraf"
                        elif last_msg.message_type == "VIDEO":
                            last_message_preview = "🎥 Video"
                        elif last_msg.message_type == "AUDIO":
                            last_message_preview = "🎤 Ses kaydı"
                
                conversations.append({
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "photo_url": photo_url,
                    "last_message": last_message_preview,
                    "last_message_time": to_iso_turkish(last_msg.created_at) if last_msg and last_msg.created_at else None,
                    "unread_count": unread_count
                })
            except Exception as e:
                # Skip this conversation if there's an error
                print(f"Error processing conversation with user {p.id}: {e}")
                continue
        
        # Sort by last message time
        conversations.sort(key=lambda x: x["last_message_time"] or "", reverse=True)
        
        return {"conversations": conversations}
        
    except Exception as e:
        print(f"Error in get_conversations: {e}")
        import traceback
        traceback.print_exc()
        # Return empty conversations instead of error
        return {"conversations": []}


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total count of unread messages for current user"""
    count = (
        db.query(Message)
        .filter(
            Message.receiver_id == current_user.id,
            Message.read_at == None
        )
        .count()
    )
    return {"unread_count": count}


@router.get("")
def get_messages(
    other_user_id: str,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if limit > 100:
        limit = 100

    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
            )
        )
        .order_by(Message.created_at.asc())  # Changed to asc for chronological order
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    
    # Mark messages from other user as read
    unread_messages = (
        db.query(Message)
        .filter(
            Message.sender_id == other_user_id,
            Message.receiver_id == current_user.id,
            Message.read_at == None
        )
        .all()
    )
    
    for msg in unread_messages:
        msg.read_at = datetime.utcnow()
    
    if unread_messages:
        db.commit()
    
    # Serialize messages
    messages_data = []
    for msg in messages:
        messages_data.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "message_type": msg.message_type if hasattr(msg, 'message_type') else "TEXT",
            "file_url": msg.file_url if hasattr(msg, 'file_url') else None,
            "file_name": msg.file_name if hasattr(msg, 'file_name') else None,
            "duration": msg.duration if hasattr(msg, 'duration') else None,
            "read_at": to_iso_turkish(msg.read_at) if msg.read_at else None,
            "created_at": to_iso_turkish(msg.created_at) if msg.created_at else None,
            "is_mine": msg.sender_id == current_user.id
        })

    return {"messages": messages_data}


@router.post("")
def send_message(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # For media messages, content can be empty string instead of None
    content = body.get("content", "")
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=body["receiver_id"],
        content=content if content else "",  # Ensure it's never None
        message_type=body.get("message_type", "TEXT"),
        file_url=body.get("file_url"),
        file_name=body.get("file_name"),
        duration=body.get("duration")
    )
    db.add(message)
    
    # Create notification if service is available
    if NOTIFICATIONS_ENABLED:
        try:
            notification_text = body.get("content", "")
            if body.get("message_type") == "IMAGE":
                notification_text = "📷 Fotoğraf gönderdi"
            elif body.get("message_type") == "VIDEO":
                notification_text = "🎥 Video gönderdi"
            elif body.get("message_type") == "AUDIO":
                notification_text = "🎤 Ses kaydı gönderdi"
            
            create_notification(
                db,
                body["receiver_id"],
                "MESSAGE",
                "Yeni mesaj",
                notification_text[:50],
                f"/messages?with={current_user.id}"
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
    
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "message_type": message.message_type,
        "file_url": message.file_url,
        "file_name": message.file_name,
        "duration": message.duration,
        "created_at": to_iso_turkish(message.created_at) if message.created_at else None,
        "is_mine": True
    }


@router.patch("/{message_id}/read")
def mark_message_read(
    message_id: str,
    current_user: User = Depends(get_current_user),  # Changed from require_verified
    db: Session = Depends(get_db)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(404, "Mesaj bulunamadı")
    if message.receiver_id != current_user.id:
        raise HTTPException(403, "Bu mesajı okuma yetkiniz yok")
    
    message.read_at = datetime.utcnow()
    db.commit()
    return {"message": "Mesaj okundu olarak işaretlendi"}
