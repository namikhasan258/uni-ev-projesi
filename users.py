# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db, User, Profile
from core.auth import get_current_user  # Changed from require_verified
import os
import aiofiles
from cuid2 import cuid_wrapper

router = APIRouter(prefix="/api/users", tags=["users"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB for profile photos

cuid_generator = cuid_wrapper()


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create profile if it doesn't exist (for existing users)
    if not current_user.profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return current_user.profile


@router.get("/{user_id}")
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get basic user info by ID (for messaging and profiles)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role": user.role
    }


@router.get("/{user_id}/profile")
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile by user ID (public view)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    if not user.profile:
        raise HTTPException(404, "Profil bulunamadı")
    
    profile = user.profile
    return {
        "bio": profile.bio,
        "photo_url": profile.photo_url,
        "budget_min": profile.budget_min,
        "budget_max": profile.budget_max,
        "smoking_ok": profile.smoking_ok,
        "pet_ok": profile.pet_ok,
        "sleep_schedule": profile.sleep_schedule,
        "cleanliness": profile.cleanliness
    }


@router.put("/profile")
def update_profile(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    
    for field in ("bio", "photo_url", "budget_min", "budget_max", "smoking_ok", "pet_ok", "sleep_schedule", "cleanliness", "name_display_format"):
        if field in body:
            setattr(profile, field, body[field])
    
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/profile/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo"""
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(400, "Geçersiz dosya türü. Sadece resim dosyaları yüklenebilir.")
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Dosya boyutu 5 MB'dan büyük olamaz")
    
    # Generate unique filename
    filename = f"profile_{current_user.id}_{cuid_generator()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    # Update profile
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    
    # Delete old photo if exists
    if profile.photo_url and profile.photo_url.startswith('/uploads/'):
        old_path = profile.photo_url.replace('/uploads/', '')
        old_filepath = os.path.join(UPLOAD_DIR, old_path)
        if os.path.exists(old_filepath):
            try:
                os.remove(old_filepath)
            except:
                pass
    
    profile.photo_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(profile)
    
    return {"url": profile.photo_url, "message": "Profil fotoğrafı güncellendi"}
