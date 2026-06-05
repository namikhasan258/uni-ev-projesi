"""
Create test accounts for UniEv platform
- 5 Students: student1@UniEv.com to student5@UniEv.com (password: student12345)
- 5 Landlords: landlord1@UniEv.com to landlord5@UniEv.com (password: landlord12345)
- 1 Admin: admin1@UniEv.com (password: admin12345)
"""

import sys
from sqlalchemy.orm import Session
from database import SessionLocal, User, Profile
from core.security import hash_password
from datetime import datetime
import uuid

def create_test_accounts():
    db = SessionLocal()
    
    try:
        print("🚀 Creating test accounts for UniEv...")
        print("=" * 60)
        
        # Student test data
        students_data = [
            {
                "first_name": "Ahmet",
                "last_name": "Yılmaz",
                "phone": "+905551234567",
                "university": "İstanbul Teknik Üniversitesi",
                "department": "Bilgisayar Mühendisliği",
                "bio": "3. sınıf öğrencisiyim. Temiz ve düzenli bir ev arıyorum. İTÜ Bilgisayar Mühendisliği.",
                "budget": 5000,
                "sleep_schedule": "EARLY_BIRD",
                "cleanliness": "HIGH",
                "smoking": False,
                "pets": False
            },
            {
                "first_name": "Ayşe",
                "last_name": "Demir",
                "phone": "+905551234568",
                "university": "Boğaziçi Üniversitesi",
                "department": "Endüstri Mühendisliği",
                "bio": "Sessiz ve sakin bir ortam tercih ediyorum. Çalışkan bir öğrenciyim. Boğaziçi Endüstri Mühendisliği.",
                "budget": 6000,
                "sleep_schedule": "NIGHT_OWL",
                "cleanliness": "HIGH",
                "smoking": False,
                "pets": True
            },
            {
                "first_name": "Mehmet",
                "last_name": "Kaya",
                "phone": "+905551234569",
                "university": "Orta Doğu Teknik Üniversitesi",
                "department": "Elektrik-Elektronik Mühendisliği",
                "bio": "Sosyal bir insanım, ev arkadaşlarıyla vakit geçirmeyi severim. ODTÜ Elektrik-Elektronik Mühendisliği.",
                "budget": 4500,
                "sleep_schedule": "FLEXIBLE",
                "cleanliness": "MEDIUM",
                "smoking": False,
                "pets": False
            },
            {
                "first_name": "Zeynep",
                "last_name": "Şahin",
                "phone": "+905551234570",
                "university": "Hacettepe Üniversitesi",
                "department": "Tıp Fakültesi",
                "bio": "Tıp öğrencisiyim, sessiz çalışma ortamına ihtiyacım var. Hacettepe Tıp Fakültesi.",
                "budget": 7000,
                "sleep_schedule": "EARLY_BIRD",
                "cleanliness": "HIGH",
                "smoking": False,
                "pets": False
            },
            {
                "first_name": "Can",
                "last_name": "Özdemir",
                "phone": "+905551234571",
                "university": "Koç Üniversitesi",
                "department": "İşletme",
                "bio": "Spor yapmayı seven, aktif bir öğrenciyim. Koç Üniversitesi İşletme.",
                "budget": 8000,
                "sleep_schedule": "EARLY_BIRD",
                "cleanliness": "MEDIUM",
                "smoking": False,
                "pets": True
            }
        ]
        
        # Landlord test data
        landlords_data = [
            {
                "first_name": "Hasan",
                "last_name": "Çelik",
                "phone": "+905559876543",
                "bio": "15 yıldır öğrencilere ev kiralıyorum. Güvenilir ve sorumlu bir ev sahibiyim."
            },
            {
                "first_name": "Fatma",
                "last_name": "Aydın",
                "phone": "+905559876544",
                "bio": "Üniversite yakınında dairelerim var. Öğrencilere özel fiyatlar."
            },
            {
                "first_name": "Ali",
                "last_name": "Yıldız",
                "phone": "+905559876545",
                "bio": "Merkezi konumda, ulaşımı kolay evlerim mevcut."
            },
            {
                "first_name": "Emine",
                "last_name": "Koç",
                "phone": "+905559876546",
                "bio": "Temiz ve bakımlı evler. Öğrenci dostu ev sahibi."
            },
            {
                "first_name": "Mustafa",
                "last_name": "Arslan",
                "phone": "+905559876547",
                "bio": "Güvenli mahallelerde, öğrencilere uygun fiyatlı konutlar."
            }
        ]
        
        # Create 5 Students
        print("\n📚 Creating STUDENT accounts...")
        print("-" * 60)
        for i, student_data in enumerate(students_data, 1):
            email = f"student{i}@UniEv.com"
            
            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"⚠️  Student {i}: {email} already exists, skipping...")
                continue
            
            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=hash_password("student12345"),
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                phone=student_data["phone"],
                role="STUDENT",
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                bio=student_data["bio"],
                budget_min=student_data["budget"] - 1000,
                budget_max=student_data["budget"] + 1000,
                sleep_schedule=student_data["sleep_schedule"],
                cleanliness=student_data["cleanliness"],
                smoking_ok=student_data["smoking"],
                pet_ok=student_data["pets"]
            )
            db.add(profile)
            
            print(f"✅ Student {i}: {email}")
            print(f"   Name: {student_data['first_name']} {student_data['last_name']}")
            print(f"   Budget: ₺{student_data['budget']}")
            print(f"   Password: student12345")
            print()
        
        # Create 5 Landlords
        print("\n🏠 Creating LANDLORD accounts...")
        print("-" * 60)
        for i, landlord_data in enumerate(landlords_data, 1):
            email = f"landlord{i}@UniEv.com"
            
            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"⚠️  Landlord {i}: {email} already exists, skipping...")
                continue
            
            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=hash_password("landlord12345"),
                first_name=landlord_data["first_name"],
                last_name=landlord_data["last_name"],
                phone=landlord_data["phone"],
                role="LANDLORD",
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                bio=landlord_data["bio"]
            )
            db.add(profile)
            
            print(f"✅ Landlord {i}: {email}")
            print(f"   Name: {landlord_data['first_name']} {landlord_data['last_name']}")
            print(f"   Password: landlord12345")
            print()
        
        # Create 1 Admin
        print("\n👑 Creating ADMIN account...")
        print("-" * 60)
        admin_email = "admin1@UniEv.com"
        
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"⚠️  Admin: {admin_email} already exists, skipping...")
        else:
            admin = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                password_hash=hash_password("admin12345"),
                first_name="Admin",
                last_name="UniEv",
                phone="+905550000000",
                role="ADMIN",
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(admin)
            db.flush()
            
            # Create profile
            profile = Profile(
                user_id=admin.id,
                bio="UniEv Platform Yöneticisi"
            )
            db.add(profile)
            
            print(f"✅ Admin: {admin_email}")
            print(f"   Name: Admin UniEv")
            print(f"   Password: admin12345")
            print()
        
        db.commit()
        
        print("=" * 60)
        print("✅ Test accounts created successfully!")
        print("\n📋 SUMMARY:")
        print("-" * 60)
        print("STUDENTS (5):")
        for i in range(1, 6):
            print(f"  • student{i}@UniEv.com / student12345")
        print("\nLANDLORDS (5):")
        for i in range(1, 6):
            print(f"  • landlord{i}@UniEv.com / landlord12345")
        print("\nADMIN (1):")
        print(f"  • admin1@UniEv.com / admin12345")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_accounts()
