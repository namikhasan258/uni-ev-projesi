# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import re
from database import get_db, User, UserConsent, LoginHistory
from core.security import hash_password, verify_password
from core.auth import create_token, get_current_user
from services.email_service import (
    send_verification_email, 
    send_reset_email,
    send_verification_code_email,
    send_password_reset_code_email,
    generate_verification_code
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 30
VERIFICATION_CODE_EXPIRY_MINUTES = 15


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@router.post("/register", status_code=201)
async def register(body: dict, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Register a new user with email verification
    
    Required fields:
    - email: Valid email address
    - password: Min 8 chars, 1 digit
    - first_name: First name
    - last_name: Last name
    - birth_date: Must be 18+
    - accept_terms: Must be true
    - accept_kvkk: Must be true
    """
    
    # --- STRICT VALIDATIONS ---
    
    # 1. Email validation
    email = body.get("email", "").strip().lower()
    if not email:
        raise HTTPException(400, "E-posta adresi gereklidir")
    if not is_valid_email(email):
        raise HTTPException(400, "Geçerli bir e-posta adresi giriniz")
    
    # 2. Password validation
    password = body.get("password", "")
    if not password:
        raise HTTPException(400, "Şifre gereklidir")
    if len(password) < 8:
        raise HTTPException(400, "Şifre en az 8 karakter olmalıdır")
    if not any(c.isdigit() for c in password):
        raise HTTPException(400, "Şifre en az bir rakam içermelidir")
    
    # 3. Name validation
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    if not first_name:
        raise HTTPException(400, "Ad gereklidir")
    if not last_name:
        raise HTTPException(400, "Soyad gereklidir")
    
    # 4. Birth date and age validation (18+)
    birth_date_str = body.get("birth_date")
    if not birth_date_str:
        raise HTTPException(400, "Doğum tarihi gereklidir")
    
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı (YYYY-MM-DD)")
    
    age = (datetime.utcnow() - birth_date).days // 365
    if age < 18:
        raise HTTPException(400, "Kayıt için 18 yaşından büyük olmanız gereklidir")
    
    # 5. Terms and KVKK acceptance (STRICT)
    accept_terms = body.get("accept_terms")
    accept_kvkk = body.get("accept_kvkk")
    
    if accept_terms is not True:
        raise HTTPException(400, "Kullanım koşullarını kabul etmelisiniz")
    if accept_kvkk is not True:
        raise HTTPException(400, "KVKK aydınlatma metnini kabul etmelisiniz")
    
    # 6. Check if email already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Bu e-posta adresi zaten kayıtlı")
    
    # 7. Check if phone already exists (if provided)
    phone = body.get("phone")
    if phone:
        phone = phone.strip() if isinstance(phone, str) else None
    else:
        phone = None
    
    if phone:
        if db.query(User).filter(User.phone == phone).first():
            raise HTTPException(400, "Bu telefon numarası zaten kayıtlı")
    
    # --- CREATE USER ---
    
    # Generate verification token (UUID)
    verification_token = secrets.token_urlsafe(32)
    
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        phone=phone,
        role=body.get("role", "STUDENT"),
        email_verification_token=verification_token,
        kvkk_consent_at=datetime.utcnow(),
        is_verified=False,  # MUST verify email
    )
    
    try:
        db.add(user)
        db.flush()
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "unique constraint" in error_msg and "phone" in error_msg:
            raise HTTPException(400, "Bu telefon numarası zaten kayıtlı")
        elif "unique constraint" in error_msg and "email" in error_msg:
            raise HTTPException(400, "Bu e-posta adresi zaten kayıtlı")
        else:
            raise HTTPException(500, f"Kayıt sırasında bir hata oluştu: {str(e)}")
    
    # Create default profile
    from database import Profile
    profile = Profile(user_id=user.id)
    db.add(profile)
    
    # Record KVKK consent
    consent = UserConsent(
        user_id=user.id,
        consent_type="KVKK",
        granted=True,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        version="1.0"
    )
    db.add(consent)
    
    # Record Terms consent
    terms_consent = UserConsent(
        user_id=user.id,
        consent_type="TERMS",
        granted=True,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        version="1.0"
    )
    db.add(terms_consent)
    
    db.commit()
    db.refresh(user)
    
    # Send verification email asynchronously
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    return {
        "message": "Kayıt başarılı! E-posta adresinize doğrulama bağlantısı gönderildi.",
        "email": user.email,
        "user_id": user.id,
        "is_verified": False
    }


@router.post("/login")
async def login(body: dict, request: Request, db: Session = Depends(get_db)):
    """
    Login user - allows login even if not verified
    Returns is_verified flag for frontend to handle
    """
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    
    if not email or not password:
        raise HTTPException(400, "E-posta ve şifre gereklidir")
    
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(401, "E-posta veya şifre hatalı")

    # Check suspension
    if user.is_suspended:
        raise HTTPException(403, "Hesabınız askıya alınmıştır")

    # Check account lockout
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(403, f"Hesabınız {remaining} dakika boyunca kilitlidir")

    # Verify password
    if not verify_password(password, user.password_hash):
        user.login_attempts += 1
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.login_attempts = 0

        # Log failed attempt
        log = LoginHistory(
            user_id=user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            fail_reason="WRONG_PASSWORD"
        )
        db.add(log)
        db.commit()
        raise HTTPException(401, "E-posta veya şifre hatalı")

    # Success — reset attempts
    user.login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()

    log = LoginHistory(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        success=True
    )
    db.add(log)
    db.commit()

    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_verified": user.is_verified  # IMPORTANT: Frontend must check this
        },
        "is_verified": user.is_verified  # Also at top level for easy access
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "is_suspended": current_user.is_suspended
    }


@router.put("/update-phone")
def update_phone(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user phone number"""
    phone = body.get("phone", "").strip()
    
    # Check if phone is already taken by another user
    if phone:
        existing = db.query(User).filter(User.phone == phone, User.id != current_user.id).first()
        if existing:
            raise HTTPException(400, "Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor")
    
    current_user.phone = phone if phone else None
    db.commit()
    
    return {"message": "Telefon numarası güncellendi", "phone": current_user.phone}


@router.put("/update-email")
def update_email(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user email address"""
    new_email = body.get("email", "").strip().lower()
    
    if not new_email:
        raise HTTPException(400, "E-posta adresi gereklidir")
    
    # Check if email is already taken by another user
    existing = db.query(User).filter(User.email == new_email, User.id != current_user.id).first()
    if existing:
        raise HTTPException(400, "Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor")
    
    current_user.email = new_email
    current_user.is_verified = False  # Require re-verification
    db.commit()
    
    return {"message": "E-posta adresi güncellendi. Lütfen yeni adresinizi doğrulayın.", "email": current_user.email}


@router.put("/update-name")
def update_name(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user name"""
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    
    if not first_name or not last_name:
        raise HTTPException(400, "Ad ve soyad gereklidir")
    
    current_user.first_name = first_name
    current_user.last_name = last_name
    db.commit()
    
    return {
        "message": "İsim güncellendi",
        "first_name": current_user.first_name,
        "last_name": current_user.last_name
    }


@router.post("/verify-email-code")
def verify_email_code(body: dict, db: Session = Depends(get_db)):
    """Verify email using 6-digit code"""
    email = body.get("email", "").strip().lower()
    code = body.get("code", "").strip()
    
    if not email or not code:
        raise HTTPException(400, "E-posta ve kod gereklidir")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    if user.is_verified:
        raise HTTPException(400, "E-posta zaten doğrulanmış")
    
    # Check if code exists and not expired
    if not user.email_verification_code:
        raise HTTPException(400, "Doğrulama kodu bulunamadı. Lütfen yeni kod isteyin.")
    
    if user.email_verification_code_expires and user.email_verification_code_expires < datetime.utcnow():
        raise HTTPException(400, "Doğrulama kodunun süresi dolmuş. Lütfen yeni kod isteyin.")
    
    # Verify code
    if user.email_verification_code != code:
        raise HTTPException(400, "Geçersiz doğrulama kodu")
    
    # Mark as verified
    user.is_verified = True
    user.email_verification_code = None
    user.email_verification_code_expires = None
    user.email_verification_token = None
    db.commit()
    
    # Return token for automatic login
    return {
        "message": "E-posta başarıyla doğrulandı!",
        "access_token": create_token(user),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_verified": user.is_verified
        }
    }


@router.post("/resend-verification-code")
async def resend_verification_code(body: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Resend verification code to email"""
    email = body.get("email", "").strip().lower()
    
    if not email:
        raise HTTPException(400, "E-posta gereklidir")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    if user.is_verified:
        raise HTTPException(400, "E-posta zaten doğrulanmış")
    
    # Generate new code
    verification_code = generate_verification_code()
    code_expires = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES)
    
    user.email_verification_code = verification_code
    user.email_verification_code_expires = code_expires
    db.commit()
    
    # Send email
    background_tasks.add_task(
        send_verification_code_email,
        user.email,
        verification_code,
        user.first_name
    )
    
    return {"message": "Yeni doğrulama kodu e-posta adresinize gönderildi"}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify email using token from email link
    
    GET /api/auth/verify-email?token=XYZ
    
    On success: redirects to /verify-success
    On error: returns JSON error
    """
    from fastapi.responses import RedirectResponse
    
    if not token:
        raise HTTPException(400, "Doğrulama token'ı gereklidir")
    
    print(f"🔍 Looking for user with token: {token[:20]}...")
    
    # Find user by token
    user = db.query(User).filter(User.email_verification_token == token).first()
    
    if not user:
        print(f"❌ No user found with token: {token[:20]}...")
        # Check if any users exist with tokens
        users_with_tokens = db.query(User).filter(User.email_verification_token != None).all()
        print(f"📊 Found {len(users_with_tokens)} users with verification tokens")
        if users_with_tokens:
            for u in users_with_tokens[:3]:  # Show first 3
                print(f"  - User {u.email}: token starts with {u.email_verification_token[:20] if u.email_verification_token else 'None'}...")
        raise HTTPException(404, "Geçersiz doğrulama bağlantısı. Token bulunamadı.")
    
    print(f"✅ Found user: {user.email}")
    
    # Check if already verified
    if user.is_verified:
        print(f"ℹ️ User {user.email} already verified")
        # Already verified - redirect to success page anyway
        return RedirectResponse(url="/verify-success", status_code=302)
    
    # Mark as verified
    print(f"✅ Verifying user: {user.email}")
    user.is_verified = True
    user.email_verification_token = None  # Invalidate token
    db.commit()
    print(f"✅ User {user.email} verified successfully!")
    
    # Redirect to success page
    return RedirectResponse(url="/verify-success", status_code=302)


@router.post("/resend-verification")
async def resend_verification(body: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Resend verification email with new token
    
    POST /resend-verification
    Body: {"email": "user@example.com"}
    """
    email = body.get("email", "").strip().lower()
    
    if not email:
        raise HTTPException(400, "E-posta adresi gereklidir")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists (security)
        return {"message": "Eğer bu e-posta kayıtlıysa, doğrulama bağlantısı gönderildi"}
    
    if user.is_verified:
        raise HTTPException(400, "E-posta adresi zaten doğrulanmış")
    
    # Generate new token
    verification_token = secrets.token_urlsafe(32)
    
    user.email_verification_token = verification_token
    db.commit()
    
    # Send email
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    return {"message": "Yeni doğrulama bağlantısı e-posta adresinize gönderildi"}


@router.post("/forgot-password")
async def forgot_password(body: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Send password reset link to email
    
    New simplified flow:
    1. User enters email
    2. System sends email with reset link
    3. User clicks link and enters new password
    """
    email = body.get("email", "").strip().lower()
    
    if not email:
        raise HTTPException(400, "E-posta gereklidir")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if email exists (security)
        return {"message": "Eğer bu e-posta kayıtlıysa, şifre sıfırlama bağlantısı gönderildi"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    user.password_reset_token = reset_token
    user.password_reset_expires = reset_expires
    db.commit()
    
    # Send email with reset link
    background_tasks.add_task(
        send_reset_email,
        user.email,
        reset_token,
        user.first_name
    )
    
    return {"message": "Eğer bu e-posta kayıtlıysa, şifre sıfırlama bağlantısı gönderildi"}


@router.post("/verify-reset-code")
def verify_reset_code(body: dict, db: Session = Depends(get_db)):
    """Verify password reset code"""
    email = body.get("email", "").strip().lower()
    code = body.get("code", "").strip()
    
    if not email or not code:
        raise HTTPException(400, "E-posta ve kod gereklidir")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(400, "Geçersiz kod")
    
    # Check if code exists and not expired
    if not user.password_reset_code:
        raise HTTPException(400, "Şifre sıfırlama kodu bulunamadı")
    
    if user.password_reset_code_expires and user.password_reset_code_expires < datetime.utcnow():
        raise HTTPException(400, "Kodun süresi dolmuş. Lütfen yeni kod isteyin.")
    
    # Verify code
    if user.password_reset_code != code:
        raise HTTPException(400, "Geçersiz kod")
    
    # Generate temporary token for password reset
    temp_token = secrets.token_urlsafe(32)
    user.password_reset_token = temp_token
    user.password_reset_expires = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    
    return {
        "message": "Kod doğrulandı",
        "reset_token": temp_token
    }


@router.post("/reset-password-with-code")
def reset_password_with_code(body: dict, db: Session = Depends(get_db)):
    """Reset password using verified code token"""
    reset_token = body.get("reset_token", "").strip()
    new_password = body.get("new_password", "").strip()
    
    if not reset_token or not new_password:
        raise HTTPException(400, "Token ve yeni şifre gereklidir")
    
    user = db.query(User).filter(User.password_reset_token == reset_token).first()
    if not user or not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        raise HTTPException(400, "Geçersiz veya süresi dolmuş token")
    
    # Validate password
    if len(new_password) < 8 or not any(c.isdigit() for c in new_password):
        raise HTTPException(400, "Şifre en az 8 karakter ve bir rakam içermelidir")
    
    # Update password
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.password_reset_code = None
    user.password_reset_code_expires = None
    user.token_version += 1
    user.login_attempts = 0
    user.locked_until = None
    db.commit()
    
    return {"message": "Şifreniz başarıyla güncellendi"}


@router.post("/reset-password")
def reset_password(body: dict, db: Session = Depends(get_db)):
    """
    Reset password using token from email link
    
    POST /api/auth/reset-password
    Body: {"token": "...", "new_password": "..."}
    """
    token = body.get("token", "").strip()
    new_password = body.get("new_password", "").strip()
    
    if not token or not new_password:
        raise HTTPException(400, "Token ve yeni şifre gereklidir")
    
    # Find user by reset token
    user = db.query(User).filter(User.password_reset_token == token).first()
    
    if not user:
        raise HTTPException(400, "Geçersiz sıfırlama bağlantısı")
    
    # Check if token expired
    if not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        raise HTTPException(400, "Sıfırlama bağlantısının süresi dolmuş. Lütfen yeni bağlantı isteyin.")
    
    # Validate password
    if len(new_password) < 8 or not any(c.isdigit() for c in new_password):
        raise HTTPException(400, "Şifre en az 8 karakter ve bir rakam içermelidir")
    
    # Update password
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.token_version += 1
    user.login_attempts = 0
    user.locked_until = None
    db.commit()
    
    return {"message": "Şifreniz başarıyla güncellendi"}


@router.post("/reset-password-security")
def reset_password_security(body: dict, db: Session = Depends(get_db)):
    """Reset password using security questions (email, full name, birth date)"""
    email = body.get("email", "").strip().lower()
    full_name = body.get("full_name", "").strip()
    birth_date_str = body.get("birth_date", "").strip()
    new_password = body.get("new_password", "").strip()
    
    if not email or not full_name or not birth_date_str or not new_password:
        raise HTTPException(400, "Tüm alanlar zorunludur")
    
    # Validate new password meets requirements (FR-03)
    if len(new_password) < 8 or not any(c.isdigit() for c in new_password):
        raise HTTPException(400, "Şifre en az 8 karakter ve bir rakam içermelidir")
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(400, "Bilgileriniz eşleşmiyor")
    
    # Verify full name (case-insensitive, handle extra spaces)
    user_full_name = f"{user.first_name} {user.last_name}".strip().lower()
    provided_full_name = " ".join(full_name.split()).lower()  # Normalize spaces
    
    if user_full_name != provided_full_name:
        raise HTTPException(400, "Bilgileriniz eşleşmiyor")
    
    # Verify birth date
    try:
        provided_birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı")
    
    if not user.birth_date or user.birth_date.date() != provided_birth_date.date():
        raise HTTPException(400, "Bilgileriniz eşleşmiyor")
    
    # All security questions match - hash and save the new password
    user.password_hash = hash_password(new_password)
    user.token_version += 1  # Invalidate existing tokens
    user.login_attempts = 0  # Reset login attempts
    user.locked_until = None  # Unlock account if locked
    db.commit()
    
    return {"message": "Şifreniz başarıyla sıfırlandı"}


@router.delete("/account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all related data"""
    # Note: Cascade delete should handle related records (Profile, Listing, Message, etc.)
    # based on database relationships defined in database.py
    
    user_id = current_user.id
    user_email = current_user.email
    
    # Delete the user (cascade should handle related data)
    db.delete(current_user)
    db.commit()
    
    return {"message": f"Hesap başarıyla silindi: {user_email}"}
