# routers/reports.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Report, Listing, User, Message
from core.auth import require_verified, get_current_user, require_admin
from datetime import datetime

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("")
def create_report(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == body["listing_id"]).first()
    if not listing:
        raise HTTPException(404, "İlan bulunamadı")
    
    report = Report(
        listing_id=body["listing_id"],
        reporter_id=current_user.id,
        report_type=body["report_type"],
        description=body.get("description")
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "message": "Rapor başarıyla gönderildi"}


@router.get("")
def get_reports(
    status: str = "PENDING",
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all reports (admin only)"""
    reports = db.query(Report).filter(Report.status == status).order_by(Report.created_at.desc()).all()
    
    reports_data = []
    for report in reports:
        reporter = db.query(User).filter(User.id == report.reporter_id).first()
        listing = db.query(Listing).filter(Listing.id == report.listing_id).first()
        
        reports_data.append({
            "id": report.id,
            "listing_id": report.listing_id,
            "listing_title": listing.title if listing else None,
            "reporter_id": report.reporter_id,
            "reporter_name": f"{reporter.first_name} {reporter.last_name}" if reporter else "Anonim",
            "report_type": report.report_type,
            "description": report.description,
            "status": report.status,
            "created_at": report.created_at.isoformat() if report.created_at else None
        })
    
    return {"reports": reports_data}


@router.post("/{report_id}/approve")
def approve_report(
    report_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a report and suspend the listing (admin only)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    
    # Business rule İK-25: Cannot re-resolve an already resolved report
    if report.status != "PENDING":
        raise HTTPException(400, "Bu rapor zaten çözümlenmiştir")
    
    # Update report status
    report.status = "APPROVED"
    report.resolved_at = datetime.utcnow()
    report.resolved_by = current_user.id
    
    # Suspend the listing
    if report.listing_id:
        listing = db.query(Listing).filter(Listing.id == report.listing_id).first()
        if listing:
            listing.status = "SUSPENDED"
    
    db.commit()
    return {"message": "Rapor onaylandı ve ilan askıya alındı"}


@router.post("/{report_id}/reject")
def reject_report(
    report_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject a report (admin only)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    
    # Business rule İK-25: Cannot re-resolve an already resolved report
    if report.status != "PENDING":
        raise HTTPException(400, "Bu rapor zaten çözümlenmiştir")
    
    report.status = "REJECTED"
    report.resolved_at = datetime.utcnow()
    report.resolved_by = current_user.id
    
    db.commit()
    return {"message": "Rapor reddedildi"}
