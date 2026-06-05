# create_admin.py
import os
from database import SessionLocal, User, create_tables
from core.security import hash_password
from cuid2 import cuid_wrapper
from datetime import datetime
import getpass

cuid_generator = cuid_wrapper()

def create_admin():
    create_tables()
    db = SessionLocal()
    try:
        email = input("Admin e-posta: ")
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"HATA: {email} zaten kayıtlı")
            return

        first_name = input("Ad: ")
        last_name = input("Soyad: ")
        password = getpass.getpass("Şifre (gizli): ")

        admin = User(
            id=cuid_generator(),
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role="ADMIN",
            is_verified=True,
            kvkk_consent_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        print(f"Admin hesabı oluşturuldu: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
