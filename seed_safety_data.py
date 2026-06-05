#!/usr/bin/env python3
"""
SafetyMap Seed Data Script
===========================
This script populates the SafetyMapPoint table with sample safety data
for major Turkish cities. This is seed data for development/demo purposes.

Usage:
    python seed_safety_data.py

Note: This script should be run after database tables are created.
"""

import os
import sys
from datetime import datetime

# Set default environment variables before imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./uniev.db")

from database import SessionLocal, SafetyMapPoint, create_tables


def seed_safety_data():
    """Populate SafetyMapPoint table with sample data for Turkish cities"""
    
    # Create tables if they don't exist
    create_tables()
    
    db = SessionLocal()
    
    # Check if data already exists
    existing_count = db.query(SafetyMapPoint).count()
    if existing_count > 0:
        print(f"⚠️  SafetyMapPoint table already has {existing_count} records.")
        response = input("Do you want to clear and re-seed? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            db.close()
            return
        
        # Clear existing data
        db.query(SafetyMapPoint).delete()
        db.commit()
        print("✓ Cleared existing data")
    
    # Sample safety data for major Turkish cities
    # Format: (latitude, longitude, district, city, safety_index)
    # safety_index: 40-90 (higher = safer)
    
    safety_points = [
        # Istanbul
        (41.0082, 28.9784, "Fatih", "Istanbul", 65),
        (41.0370, 28.9850, "Beyoğlu", "Istanbul", 70),
        (41.0534, 29.0089, "Beşiktaş", "Istanbul", 75),
        (41.0766, 29.0551, "Sarıyer", "Istanbul", 80),
        (40.9929, 29.0265, "Kadıköy", "Istanbul", 78),
        (40.9667, 29.1167, "Üsküdar", "Istanbul", 72),
        (41.0255, 28.7319, "Avcılar", "Istanbul", 68),
        
        # Ankara
        (39.9334, 32.8597, "Çankaya", "Ankara", 82),
        (39.9208, 32.8541, "Kızılay", "Ankara", 75),
        (39.9500, 32.8667, "Yenimahalle", "Ankara", 70),
        (39.8667, 32.7333, "Etimesgut", "Ankara", 68),
        (39.9000, 32.8000, "Keçiören", "Ankara", 65),
        
        # Izmir
        (38.4192, 27.1287, "Konak", "Izmir", 72),
        (38.4237, 27.1428, "Alsancak", "Izmir", 78),
        (38.4667, 27.2167, "Bornova", "Izmir", 75),
        (38.3687, 27.0470, "Karşıyaka", "Izmir", 76),
        (38.4000, 27.0500, "Buca", "Izmir", 73),
        
        # Kocaeli (Izmit)
        (40.7654, 29.9404, "Merkez", "Kocaeli", 70),
        (40.7667, 29.9167, "İzmit", "Kocaeli", 72),
        (40.7833, 29.9333, "Körfez", "Kocaeli", 68),
        (40.8500, 30.0500, "Gebze", "Kocaeli", 74),
        (40.7000, 29.8500, "Gölcük", "Kocaeli", 66),
        
        # Bursa
        (40.1826, 29.0665, "Osmangazi", "Bursa", 76),
        (40.2000, 29.0667, "Nilüfer", "Bursa", 80),
        (40.1833, 29.0333, "Yıldırım", "Bursa", 72),
        
        # Antalya
        (36.8969, 30.7133, "Muratpaşa", "Antalya", 78),
        (36.8841, 30.7056, "Konyaaltı", "Antalya", 82),
        (36.9081, 30.7414, "Kepez", "Antalya", 74),
    ]
    
    print(f"\n📍 Seeding {len(safety_points)} safety data points...")
    
    for lat, lon, district, city, safety_index in safety_points:
        point = SafetyMapPoint(
            latitude=lat,
            longitude=lon,
            district=district,
            city=city,
            safety_index=safety_index,
            updated_at=datetime.utcnow()
        )
        db.add(point)
        print(f"  ✓ {city} - {district}: Safety Index {safety_index}")
    
    db.commit()
    print(f"\n✅ Successfully seeded {len(safety_points)} safety data points!")
    print(f"📊 Total records in SafetyMapPoint: {db.query(SafetyMapPoint).count()}")
    
    db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("UniEv - SafetyMap Seed Data Script")
    print("=" * 60)
    print("\nThis script will populate the SafetyMapPoint table with")
    print("sample safety data for major Turkish cities.")
    print("\n⚠️  Note: This is seed data for development/demo purposes only.")
    print("=" * 60)
    print()
    
    try:
        seed_safety_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
