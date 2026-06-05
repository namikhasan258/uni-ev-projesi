# routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from database import get_db, Rating, User
from core.auth import get_current_user

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


# Pydantic schemas for validation
class RatingCreate(BaseModel):
    rated_id: str
    rating: int = Field(ge=1, le=5, description="Rating must be between 1 and 5")
    comment: str = ""


class RatingUpdate(BaseModel):
    rating: int = Field(ge=1, le=5, description="Rating must be between 1 and 5")
    comment: str = None


@router.post("")
def create_rating(
    body: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a rating for a user (max 2 ratings per user)"""
    if body.rated_id == current_user.id:
        raise HTTPException(400, "Kendinizi değerlendiremezsiniz")
    
    # Check if user exists
    rated_user = db.query(User).filter(User.id == body.rated_id).first()
    if not rated_user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    # Count existing ratings
    existing_count = db.query(Rating).filter(
        Rating.rater_id == current_user.id,
        Rating.rated_id == body.rated_id
    ).count()
    
    if existing_count >= 2:
        raise HTTPException(400, "Bu kullanıcıyı en fazla 2 kez değerlendirebilirsiniz")
    
    # Determine rating number (1 or 2)
    rating_number = existing_count + 1
    
    # Validate rating_number is 1 or 2
    if rating_number not in [1, 2]:
        raise HTTPException(400, "rating_number 1 veya 2 olmalıdır")
    
    # Create rating
    new_rating = Rating(
        rater_id=current_user.id,
        rated_id=body.rated_id,
        rating=body.rating,
        rating_number=rating_number,
        comment=body.comment
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return {
        "id": new_rating.id,
        "rating": new_rating.rating,
        "rating_number": new_rating.rating_number,
        "comment": new_rating.comment,
        "created_at": new_rating.created_at.isoformat()
    }


@router.get("/user/{user_id}")
def get_user_ratings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all ratings for a user and calculate average"""
    # Get all ratings
    ratings = db.query(Rating).filter(Rating.rated_id == user_id).all()
    
    if not ratings:
        return {
            "average_rating": 0,
            "total_ratings": 0,
            "ratings": []
        }
    
    # Calculate average
    total = sum(r.rating for r in ratings)
    average = total / len(ratings)
    
    # Serialize ratings
    ratings_data = []
    for r in ratings:
        rater = db.query(User).filter(User.id == r.rater_id).first()
        ratings_data.append({
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "rater_name": f"{rater.first_name} {rater.last_name}" if rater else "Anonim",
            "rater_photo": rater.profile.photo_url if rater and rater.profile else None,
            "created_at": r.created_at.isoformat()
        })
    
    return {
        "average_rating": round(average, 1),
        "total_ratings": len(ratings),
        "ratings": ratings_data
    }


@router.get("/user/{user_id}/my-ratings")
def get_my_ratings_for_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's ratings for a specific user"""
    ratings = db.query(Rating).filter(
        Rating.rater_id == current_user.id,
        Rating.rated_id == user_id
    ).all()
    
    ratings_data = []
    for r in ratings:
        ratings_data.append({
            "id": r.id,
            "rating": r.rating,
            "rating_number": r.rating_number,
            "comment": r.comment,
            "created_at": r.created_at.isoformat()
        })
    
    return {
        "ratings": ratings_data,
        "can_rate_more": len(ratings) < 2
    }


@router.put("/{rating_id}")
def update_rating(
    rating_id: str,
    body: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a rating"""
    rating_obj = db.query(Rating).filter(Rating.id == rating_id).first()
    
    if not rating_obj:
        raise HTTPException(404, "Rating bulunamadı")
    
    if rating_obj.rater_id != current_user.id:
        raise HTTPException(403, "Bu rating'i düzenleme yetkiniz yok")
    
    # Update rating (Pydantic already validates 1-5 range)
    rating_obj.rating = body.rating
    
    if body.comment is not None:
        rating_obj.comment = body.comment
    
    db.commit()
    db.refresh(rating_obj)
    
    return {
        "id": rating_obj.id,
        "rating": rating_obj.rating,
        "comment": rating_obj.comment
    }


@router.delete("/{rating_id}")
def delete_rating(
    rating_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a rating"""
    rating_obj = db.query(Rating).filter(Rating.id == rating_id).first()
    
    if not rating_obj:
        raise HTTPException(404, "Rating bulunamadı")
    
    if rating_obj.rater_id != current_user.id:
        raise HTTPException(403, "Bu rating'i silme yetkiniz yok")
    
    db.delete(rating_obj)
    db.commit()
    
    return {"message": "Rating silindi"}
