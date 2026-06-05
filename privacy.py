# routers/privacy.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, User, DataRequest, UserConsent, CookiePreference
from core.auth import require_verified
import json

router = APIRouter(prefix="/api/privacy", tags=["privacy"])


@router.get("/my-data")
def get_my_data(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    # Return user data without sensitive fields
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "birth_date": current_user.birth_date,
        "phone": current_user.phone,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@router.get("/export-data")
def export_data(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    # Export all user data as JSON
    data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "birth_date": str(current_user.birth_date) if current_user.birth_date else None,
            "phone": current_user.phone,
            "role": current_user.role,
            "created_at": str(current_user.created_at)
        },
        "profile": current_user.profile.__dict__ if current_user.profile else None,
        "listings": [l.__dict__ for l in current_user.listings],
        "messages_sent": len(current_user.sent_messages),
        "messages_received": len(current_user.received_messages)
    }
    return data


@router.post("/request-deletion")
def request_deletion(
    body: dict,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    request = DataRequest(
        user_id=current_user.id,
        request_type="DELETE_ACCOUNT",
        reason=body.get("reason")
    )
    db.add(request)
    
    current_user.delete_requested_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Hesap silme talebiniz alındı"}


@router.get("/consents")
def get_consents(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    consents = db.query(UserConsent).filter(UserConsent.user_id == current_user.id).all()
    return {"consents": consents}


@router.post("/consents")
def update_consent(
    body: dict,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    consent = UserConsent(
        user_id=current_user.id,
        consent_type=body["consent_type"],
        granted=body["granted"],
        version="1.0"
    )
    db.add(consent)
    db.commit()
    return consent


@router.post("/cookie-preferences")
def save_cookie_preferences(body: dict, db: Session = Depends(get_db)):
    # Business rule İK-33: Necessary cookies cannot be changed by user
    # Always force necessary=True regardless of user input
    pref = CookiePreference(
        session_id=body.get("session_id"),
        necessary=True,  # İK-33: Always True, user cannot change this
        analytics=body.get("analytics", False),
        marketing=body.get("marketing", False),
        performance=body.get("performance", False)
    )
    db.add(pref)
    db.commit()
    return {"message": "Çerez tercihleri kaydedildi"}
