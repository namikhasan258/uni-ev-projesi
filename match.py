# routers/match.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, User
from core.auth import get_current_user  # Changed from require_verified
from services.match_service import get_matches

router = APIRouter(prefix="/api/match", tags=["match"])


@router.get("/suggestions")
def get_match_suggestions(
    current_user: User = Depends(get_current_user),  # Changed from require_verified
    db: Session = Depends(get_db)
):
    # Check if user has a profile
    if not current_user.profile:
        return {"matches": [], "has_profile": False}
    
    # Check if profile is complete (has required fields for matching)
    profile = current_user.profile
    is_complete = (
        profile.budget_min is not None and
        profile.budget_max is not None and
        profile.smoking_ok is not None and  # Can be True or False, but not None
        profile.pet_ok is not None and      # Can be True or False, but not None
        profile.sleep_schedule is not None and
        profile.sleep_schedule != "" and
        profile.cleanliness is not None and
        profile.cleanliness != ""
    )
    
    if not is_complete:
        return {"matches": [], "has_profile": True, "is_complete": False}
    
    matches = get_matches(current_user, db)
    return {"matches": matches, "has_profile": True, "is_complete": True}
