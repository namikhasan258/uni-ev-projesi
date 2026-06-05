#!/usr/bin/env python3
"""
Create test data for UniEv
- 3 test students with profiles
- 2 test landlords with listings
"""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///./uniev.db")
os.environ.setdefault("JWT_SECRET", "default-secret-change-in-production")

from database import SessionLocal, User, Profile, Listing
from core.security import hash_password
from datetime import datetime

def create_test_data():
    db = SessionLocal()
    
    try:
        print("\n=== Creating Test Data ===\n")
        
        # Check if test data already exists
        existing = db.query(User).filter(User.email.like('%test%')).first()
        if existing:
            print("⚠ Test data already exists. Delete it first if you want to recreate.")
            response = input("Delete existing test data and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return
            
            # Delete existing test users
            test_users = db.query(User).filter(User.email.like('%test%')).all()
            for user in test_users:
                db.delete(user)
            db.commit()
            print("✓ Deleted existing test data\n")
        
        # Create 3 test students
        students = []
        student_data = [
            {
                "email": "student1@test.com",
                "password": "test123",
                "first_name": "Ahmet",
                "last_name": "Yılmaz",
                "phone": "5551234567",
                "profile": {
                    "bio": "Mühendislik öğrencisiyim. Sessiz ve düzenli bir ev arkadaşı arıyorum.",
                    "budget_min": 3000,
                    "budget_max": 5000,
                    "smoking_ok": False,
                    "pet_ok": True,
                    "sleep_schedule": "EARLY_BIRD",
                    "cleanliness": "HIGH"
                }
            },
            {
                "email": "student2@test.com",
                "password": "test123",
                "first_name": "Ayşe",
                "last_name": "Demir",
                "phone": "5552345678",
                "profile": {
                    "bio": "Tıp fakültesi öğrencisiyim. Çalışkan ve sosyal biriyim.",
                    "budget_min": 4000,
                    "budget_max": 6000,
                    "smoking_ok": False,
                    "pet_ok": False,
                    "sleep_schedule": "NIGHT_OWL",
                    "cleanliness": "MEDIUM"
                }
            },
            {
                "email": "student3@test.com",
                "password": "test123",
                "first_name": "Mehmet",
                "last_name": "Kaya",
                "phone": "5553456789",
                "profile": {
                    "bio": "Bilgisayar mühendisliği öğrencisiyim. Oyun oynamayı severim.",
                    "budget_min": 2500,
                    "budget_max": 4500,
                    "smoking_ok": False,
                    "pet_ok": True,
                    "sleep_schedule": "NIGHT_OWL",
                    "cleanliness": "LOW"
                }
            }
        ]
        
        for data in student_data:
            user = User(
                email=data["email"],
                password_hash=hash_password(data["password"]),
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
                role="STUDENT",
                is_verified=True
            )
            db.add(user)
            db.flush()
            
            profile = Profile(
                user_id=user.id,
                bio=data["profile"]["bio"],
                budget_min=data["profile"]["budget_min"],
                budget_max=data["profile"]["budget_max"],
                smoking_ok=data["profile"]["smoking_ok"],
                pet_ok=data["profile"]["pet_ok"],
                sleep_schedule=data["profile"]["sleep_schedule"],
                cleanliness=data["profile"]["cleanliness"]
            )
            db.add(profile)
            students.append(user)
            
            print(f"✓ Created student: {user.first_name} {user.last_name} ({user.email})")
        
        db.commit()
        print(f"\n✓ Created {len(students)} test students with profiles\n")
        
        # Create 2 test landlords with listings
        landlords = []
        landlord_data = [
            {
                "email": "landlord1@test.com",
                "password": "test123",
                "first_name": "Fatma",
                "last_name": "Özkan",
                "phone": "5554567890",
                "listings": [
                    {
                        "title": "Üniversiteye Yakın 2+1 Daire",
                        "description": "Kampüse 5 dakika yürüme mesafesinde, yeni yapılmış, eşyalı daire. Tüm ihtiyaçlarınız için market ve ulaşım çok yakın.",
                        "price": 4500,
                        "city": "İstanbul",
                        "district": "Kadıköy",
                        "address": "Caferağa Mahallesi, Moda Caddesi No:15",
                        "rules": "Sigara içilmez. Evcil hayvan kabul edilmez. Gece 23:00'dan sonra sessizlik."
                    },
                    {
                        "title": "Geniş 3+1 Öğrenci Evi",
                        "description": "3 öğrenci için ideal, her odada çalışma masası var. Balkonlu, güneşli daire.",
                        "price": 6000,
                        "city": "İstanbul",
                        "district": "Beşiktaş",
                        "address": "Etiler Mahallesi, Nispetiye Caddesi",
                        "rules": "Parti yapılmaz. Temizlik önemlidir."
                    }
                ]
            },
            {
                "email": "landlord2@test.com",
                "password": "test123",
                "first_name": "Hasan",
                "last_name": "Çelik",
                "phone": "5555678901",
                "listings": [
                    {
                        "title": "Merkezi Konumda 1+1 Stüdyo",
                        "description": "Tek kişilik öğrenci için ideal. Metro ve otobüs durağına çok yakın. Eşyalı ve hazır.",
                        "price": 3500,
                        "city": "Ankara",
                        "district": "Çankaya",
                        "address": "Kızılay Mahallesi, Atatürk Bulvarı",
                        "rules": "Sigara içilmez. Sessiz ve düzenli yaşam."
                    }
                ]
            }
        ]
        
        for data in landlord_data:
            user = User(
                email=data["email"],
                password_hash=hash_password(data["password"]),
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
                role="LANDLORD",
                is_verified=True
            )
            db.add(user)
            db.flush()
            
            # Create profile for landlord too
            profile = Profile(user_id=user.id)
            db.add(profile)
            
            landlords.append(user)
            print(f"✓ Created landlord: {user.first_name} {user.last_name} ({user.email})")
            
            # Create listings
            for listing_data in data["listings"]:
                listing = Listing(
                    owner_id=user.id,
                    title=listing_data["title"],
                    description=listing_data["description"],
                    price=listing_data["price"],
                    city=listing_data["city"],
                    district=listing_data["district"],
                    address=listing_data.get("address"),
                    rules=listing_data.get("rules"),
                    status="ACTIVE",
                    fraud_score=20  # Low fraud score for test data
                )
                db.add(listing)
                print(f"  ✓ Created listing: {listing.title}")
        
        db.commit()
        print(f"\n✓ Created {len(landlords)} test landlords with listings\n")
        
        print("=== Test Data Created Successfully! ===\n")
        print("Test Accounts:")
        print("\nStudents (password: test123):")
        for data in student_data:
            print(f"  - {data['email']}")
        print("\nLandlords (password: test123):")
        for data in landlord_data:
            print(f"  - {data['email']}")
        
        print("\n✓ You can now:")
        print("  1. Login as any student to see matches")
        print("  2. Login as any landlord to see listings")
        print("  3. Test the matching algorithm")
        print("  4. Test messaging between users")
        
    except Exception as e:
        print(f"\n✗ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
