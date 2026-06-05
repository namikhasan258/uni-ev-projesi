# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, User, Report, Listing, AuditLog, Message, DataRequest, Notification
from core.auth import require_admin
from services.notification_service import create_notification

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/reports")
def get_reports(
    status: str = "PENDING",
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    reports = db.query(Report).filter(Report.status == status).all()
    return {"reports": reports}


@router.get("/reports/{report_id}")
def get_report(
    report_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    return report


@router.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: str,
    body: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    
    action = body["action"]  # APPROVE | SUSPEND | DELETE
    
    if action == "SUSPEND" and report.listing:
        report.listing.status = "SUSPENDED"
    elif action == "DELETE" and report.listing:
        report.listing.status = "DELETED"
    
    report.status = action
    report.resolved_at = datetime.utcnow()
    report.resolved_by = current_user.id
    
    # Create audit log
    log = AuditLog(
        admin_id=current_user.id,
        action=f"RESOLVE_REPORT_{action}",
        target_type="REPORT",
        target_id=report_id,
        details=body.get("note")
    )
    db.add(log)
    db.commit()
    
    return {"message": "Rapor çözümlendi"}


@router.get("/users")
def get_users(
    role: str = None,  # Filter by role: STUDENT, LANDLORD, or None for all
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with optional role filter"""
    try:
        query = db.query(User)
        
        if role and role in ["STUDENT", "LANDLORD", "ADMIN"]:
            query = query.filter(User.role == role)
        
        users = query.all()
        
        users_data = []
        for u in users:
            users_data.append({
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "phone": u.phone,
                "role": u.role,
                "is_verified": u.is_verified,
                "is_suspended": u.is_suspended,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None
            })
        
        return {"users": users_data, "total": len(users_data)}
        
    except Exception as e:
        print(f"Error getting users: {e}")
        import traceback
        traceback.print_exc()
        return {"users": [], "total": 0}


@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    user.is_suspended = True
    
    log = AuditLog(
        admin_id=current_user.id,
        action="SUSPEND_USER",
        target_type="USER",
        target_id=user_id
    )
    db.add(log)
    db.commit()
    
    return {"message": "Kullanıcı askıya alındı"}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    user.is_suspended = False
    
    log = AuditLog(
        admin_id=current_user.id,
        action="ACTIVATE_USER",
        target_type="USER",
        target_id=user_id
    )
    db.add(log)
    db.commit()
    
    return {"message": "Kullanıcı aktif edildi"}


@router.post("/users/{user_id}/change-role")
def change_user_role(
    user_id: str,
    body: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Change user role (STUDENT, LANDLORD, ADMIN)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    new_role = body.get("role")
    if new_role not in ["STUDENT", "LANDLORD", "ADMIN"]:
        raise HTTPException(400, "Geçersiz rol. STUDENT, LANDLORD veya ADMIN olmalıdır")
    
    old_role = user.role
    user.role = new_role
    
    # Create audit log
    log = AuditLog(
        admin_id=current_user.id,
        action="CHANGE_USER_ROLE",
        target_type="USER",
        target_id=user_id,
        details=f"Changed role from {old_role} to {new_role}"
    )
    db.add(log)
    db.commit()
    
    return {"message": f"Kullanıcı rolü {new_role} olarak değiştirildi", "new_role": new_role}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user account permanently"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    if user.role == "ADMIN":
        raise HTTPException(403, "Admin kullanıcıları silinemez")
    
    user_email = user.email
    
    # Delete user (cascade will handle related data)
    db.delete(user)
    
    # Create audit log
    log = AuditLog(
        admin_id=current_user.id,
        action="DELETE_USER",
        target_type="USER",
        target_id=user_id,
        details=f"Deleted user: {user_email}"
    )
    db.add(log)
    db.commit()
    
    return {"message": "Kullanıcı kalıcı olarak silindi"}


@router.get("/stats")
def get_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics"""
    try:
        # Total users
        total_users = db.query(User).count()
        
        # Students and landlords separately
        students_count = db.query(User).filter(User.role == "STUDENT").count()
        landlords_count = db.query(User).filter(User.role == "LANDLORD").count()
        
        # Active listings (not suspended or deleted)
        total_listings = db.query(Listing).filter(Listing.status == "ACTIVE").count()
        
        # Pending reports
        pending_reports = db.query(Report).filter(Report.status == "PENDING").count()
        
        # Total messages
        total_messages = db.query(Message).count()
        
        return {
            "total_users": total_users,
            "students_count": students_count,
            "landlords_count": landlords_count,
            "total_listings": total_listings,
            "pending_reports": pending_reports,
            "total_messages": total_messages
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        import traceback
        traceback.print_exc()
        # Return zeros instead of error
        return {
            "total_users": 0,
            "students_count": 0,
            "landlords_count": 0,
            "total_listings": 0,
            "pending_reports": 0,
            "total_messages": 0
        }



@router.patch("/data-requests/{request_id}/status")
def update_data_request_status(
    request_id: str,
    body: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update DataRequest status (PROCESSING, COMPLETED, DENIED)
    Implements full DataRequest status lifecycle from SRS Section 4.1.14
    """
    data_request = db.query(DataRequest).filter(DataRequest.id == request_id).first()
    if not data_request:
        raise HTTPException(404, "Veri talebi bulunamadı")
    
    new_status = body.get("status")
    if new_status not in ["PROCESSING", "COMPLETED", "DENIED"]:
        raise HTTPException(400, "Geçersiz durum. PROCESSING, COMPLETED veya DENIED olmalıdır")
    
    response_text = body.get("response", "")
    
    # Update data request
    old_status = data_request.status
    data_request.status = new_status
    data_request.response = response_text
    data_request.processed_by = current_user.id
    data_request.processed_at = datetime.utcnow()
    
    # Create notification for user
    notification_messages = {
        "PROCESSING": "Veri talebiniz işleme alındı",
        "COMPLETED": "Veri talebiniz tamamlandı",
        "DENIED": "Veri talebiniz reddedildi"
    }
    
    create_notification(
        db=db,
        user_id=data_request.user_id,
        notification_type="DATA_REQUEST_UPDATE",
        title=notification_messages.get(new_status, "Veri talebi güncellendi"),
        body=response_text if response_text else None,
        link=f"/privacy"
    )
    
    # Create audit log
    log = AuditLog(
        admin_id=current_user.id,
        action="UPDATE_DATA_REQUEST_STATUS",
        target_type="DATA_REQUEST",
        target_id=request_id,
        details=f"Changed status from {old_status} to {new_status}"
    )
    db.add(log)
    
    db.commit()
    
    return {
        "message": "Veri talebi durumu güncellendi",
        "status": new_status
    }
