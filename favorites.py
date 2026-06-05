# routers/favorites.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Favorite, Listing, User
from core.auth import require_verified

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("")
def get_favorites(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .all()
    )
    return {"favorites": favorites}


@router.post("")
def add_favorite(
    body: dict,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == body["listing_id"]).first()
    if not listing:
        raise HTTPException(404, "İlan bulunamadı")
    
    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.listing_id == body["listing_id"]
    ).first()
    
    if existing:
        raise HTTPException(400, "Bu ilan zaten favorilerinizde")
    
    favorite = Favorite(
        user_id=current_user.id,
        listing_id=body["listing_id"]
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{listing_id}")
def remove_favorite(
    listing_id: str,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.listing_id == listing_id
    ).first()
    
    if not favorite:
        raise HTTPException(404, "Favori bulunamadı")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Favori kaldırıldı"}
