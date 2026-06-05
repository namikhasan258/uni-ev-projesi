# routers/safety.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.safety_service import query_safety_map

router = APIRouter(prefix="/api/safety", tags=["safety"])


@router.get("/map")
def get_safety_map(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db)
):
    try:
        result = query_safety_map(lat, lon, radius_km, db)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
