# routers/listings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Listing, ListingPhoto, FraudScoreRecord, User
from core.auth import require_verified, require_landlord, get_current_user
from services.fraud_service import calculate_fraud_score

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("")
def search_listings(
    min_price: int = None,
    max_price: int = None,
    max_fraud_score: int = None,
    min_safety_index: int = None,
    city: str = None,
    owner_id: str = None,
    page: int = 1,
    limit: int = 50,  # Increased default limit to show more listings
    db: Session = Depends(get_db)
):
    if limit > 100:
        limit = 100  # Increased max limit

    query = db.query(Listing).filter(Listing.status == "ACTIVE")

    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    if max_fraud_score is not None:
        query = query.filter(Listing.fraud_score <= max_fraud_score)
    if min_safety_index is not None:
        query = query.filter(Listing.safety_index >= min_safety_index)
    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if owner_id:
        query = query.filter(Listing.owner_id == owner_id)

    total = query.count()
    listings = query.order_by(Listing.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Serialize listings to dict with photos
    listings_data = []
    for listing in listings:
        # Get photos for this listing
        photos = db.query(ListingPhoto).filter(ListingPhoto.listing_id == listing.id).order_by(ListingPhoto.order).all()
        photo_urls = [photo.url for photo in photos]
        
        print(f"Listing {listing.id} ({listing.title}): {len(photo_urls)} photos")
        if photo_urls:
            print(f"  Cover photo: {photo_urls[0]}")
        
        listings_data.append({
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "city": listing.city,
            "district": listing.district,
            "address": listing.address,
            "latitude": listing.latitude,
            "longitude": listing.longitude,
            "fraud_score": listing.fraud_score,
            "safety_index": listing.safety_index,
            "status": listing.status,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
            "photo_urls": photo_urls,
            "cover_photo": photo_urls[0] if photo_urls else None
        })

    return {"total": total, "page": page, "limit": limit, "listings": listings_data}


@router.post("", status_code=201)
def create_listing(
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_landlord)
):
    listing = Listing(
        owner_id=current_user.id,
        title=body["title"],
        description=body["description"],
        price=body["price"],
        city=body.get("city"),
        district=body.get("district"),
        address=body.get("address"),
        latitude=body.get("latitude"),
        longitude=body.get("longitude"),
        rules=body.get("rules"),
        status="ACTIVE"
    )
    db.add(listing)
    db.flush()

    # Save photos
    for i, url in enumerate(body.get("photo_urls", [])):
        photo = ListingPhoto(listing_id=listing.id, url=url, order=i)
        db.add(photo)

    db.commit()
    db.refresh(listing)

    # Calculate and save FraudScore
    score, factors = calculate_fraud_score(listing, current_user)
    listing.fraud_score = score
    record = FraudScoreRecord(listing_id=listing.id, score=score, factors=str(factors))
    db.add(record)
    db.commit()

    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "city": listing.city,
        "district": listing.district,
        "fraud_score": listing.fraud_score,
        "status": listing.status,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
    }


@router.get("/{listing_id}")
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    try:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            raise HTTPException(404, "İlan bulunamadı")
        if listing.status in ("SUSPENDED", "DELETED"):
            raise HTTPException(410, "Bu ilan artık mevcut değil")
        
        # Get owner info with profile - safely handle missing profile
        owner = db.query(User).filter(User.id == listing.owner_id).first()
        owner_photo = None
        owner_bio = None
        owner_phone = None
        owner_email = None
        owner_name = "Bilinmiyor"
        
        if owner:
            owner_name = f"{owner.first_name or ''} {owner.last_name or ''}".strip() or "Bilinmiyor"
            owner_phone = owner.phone
            owner_email = owner.email
            
            # Safely get profile data
            try:
                from database import Profile
                profile = db.query(Profile).filter(Profile.user_id == owner.id).first()
                if profile:
                    owner_photo = profile.photo_url
                    owner_bio = profile.bio
            except Exception as profile_error:
                print(f"Warning: Could not load profile: {profile_error}")
                # Continue without profile data
        
        # Get photos
        photos = db.query(ListingPhoto).filter(ListingPhoto.listing_id == listing.id).order_by(ListingPhoto.order).all()
        photo_urls = [photo.url for photo in photos]
        
        return {
            "id": str(listing.id),
            "title": str(listing.title or ""),
            "description": str(listing.description or ""),
            "price": int(listing.price) if listing.price else 0,
            "city": str(listing.city or ""),
            "district": str(listing.district or ""),
            "address": str(listing.address or "") if listing.address else None,
            "latitude": float(listing.latitude) if listing.latitude else None,
            "longitude": float(listing.longitude) if listing.longitude else None,
            "rules": str(listing.rules or "") if listing.rules else None,
            "fraud_score": int(listing.fraud_score) if listing.fraud_score else 0,
            "safety_index": int(listing.safety_index) if listing.safety_index else 0,
            "status": str(listing.status or "ACTIVE"),
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
            "owner_id": str(listing.owner_id),
            "owner_name": str(owner_name),
            "owner_photo": str(owner_photo) if owner_photo else None,
            "owner_bio": str(owner_bio) if owner_bio else None,
            "owner_phone": str(owner_phone) if owner_phone else None,
            "owner_email": str(owner_email) if owner_email else None,
            "photos": [str(url) for url in photo_urls],
            "photo_urls": [str(url) for url in photo_urls]  # Added for edit page compatibility
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_listing: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"İlan yüklenirken hata oluştu: {str(e)}")


@router.put("/{listing_id}")
def update_listing(
    listing_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_landlord)
):
    print(f"\n=== UPDATE LISTING {listing_id} ===")
    print(f"Body received: {body}")
    print(f"photo_urls in body: {'photo_urls' in body}")
    if "photo_urls" in body:
        print(f"Number of photos: {len(body['photo_urls'])}")
        print(f"Photo URLs: {body['photo_urls']}")
    
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(404, "İlan bulunamadı")
    if listing.owner_id != current_user.id:
        raise HTTPException(403, "Bu ilanı düzenleme yetkiniz yok")
    if listing.status in ("SUSPENDED", "DELETED"):
        raise HTTPException(403, "Askıya alınmış veya silinmiş ilan güncellenemez")

    for field in ("title", "description", "price", "city", "district", "address", "latitude", "longitude", "rules"):
        if field in body:
            setattr(listing, field, body[field])

    # Update photos if provided
    if "photo_urls" in body:
        print(f"Deleting existing photos for listing {listing_id}")
        # Delete existing photos
        deleted_count = db.query(ListingPhoto).filter(ListingPhoto.listing_id == listing.id).delete()
        print(f"Deleted {deleted_count} existing photos")
        
        # Add new photos
        print(f"Adding {len(body['photo_urls'])} new photos")
        for i, url in enumerate(body["photo_urls"]):
            photo = ListingPhoto(listing_id=listing.id, url=url, order=i)
            db.add(photo)
            print(f"  Photo {i}: {url}")

    db.commit()
    print("Photos committed to database")
    
    # Get the updated photos to return
    updated_photos = db.query(ListingPhoto).filter(ListingPhoto.listing_id == listing.id).order_by(ListingPhoto.order).all()
    updated_photo_urls = [photo.url for photo in updated_photos]
    print(f"Photos now in database: {updated_photo_urls}")

    # Recalculate FraudScore on update
    score, factors = calculate_fraud_score(listing, current_user)
    listing.fraud_score = score
    record = FraudScoreRecord(listing_id=listing.id, score=score, factors=str(factors))
    db.add(record)
    db.commit()
    
    print(f"=== UPDATE COMPLETE ===\n")

    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "city": listing.city,
        "district": listing.district,
        "fraud_score": listing.fraud_score,
        "status": listing.status,
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
        "photo_urls": updated_photo_urls,  # ADDED: Return the photos so frontend can verify
        "photo_count": len(updated_photo_urls)  # ADDED: Count for easy verification
    }


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_landlord)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(404, "İlan bulunamadı")
    if listing.owner_id != current_user.id:
        raise HTTPException(403, "Bu ilanı silme yetkiniz yok")

    listing.status = "DELETED"
    db.commit()
    return {"message": "İlan başarıyla silindi"}
