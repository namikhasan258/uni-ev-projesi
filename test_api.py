"""Quick test to verify listings API"""
from database import SessionLocal, Listing

db = SessionLocal()

# Get all ACTIVE listings
active_listings = db.query(Listing).filter(Listing.status == "ACTIVE").all()

print(f"✅ Total ACTIVE listings: {len(active_listings)}")
print("\n📋 Listings:")
for i, listing in enumerate(active_listings, 1):
    print(f"{i}. {listing.title}")
    print(f"   City: {listing.city}, District: {listing.district}")
    print(f"   Price: ₺{listing.price:,}")
    print(f"   Status: {listing.status}")
    print()

db.close()
