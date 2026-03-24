from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import BackgroundTasks
from app.services.email_service import process_email

from app.schemas.email import EmailCreate, EmailOut
from app.models.email import Email
from app.api.deps import get_db, get_current_user
from app.services.spam import predict_spam
from app.models.user import User


router = APIRouter(prefix="/emails", tags=["Emails"])

@router.post("/send", response_model=EmailOut, status_code=201)
def send_email(
    email: EmailCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_email = Email(
        sender_id=current_user.id,
        receiver_id=email.receiver_id,
        subject=email.subject,
        body=email.body,
        status="pending",
        folder="pending"
    )

    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    background_tasks.add_task(process_email, new_email.id)

    return new_email

@router.get("/inbox", response_model=list[EmailOut])
def get_inbox(
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "inbox",
        Email.status == "delivered"
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()
    
    
@router.get("/spam", response_model=list[EmailOut])
def get_spam(
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "spam",
        Email.status == "delivered"
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()
    
@router.get("/sent", response_model=list[EmailOut])
def get_sent(
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Email).filter(
        Email.sender_id == current_user.id
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()
    
@router.get("/{email_id}", response_model=EmailOut)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if email.sender_id != current_user.id and email.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 📖 Auto mark as read (only for receiver)
    if email.receiver_id == current_user.id:
        email.is_read = True
        db.commit()

    return email

@router.patch("/{email_id}/read")
def mark_read(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if email.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    email.is_read = True
    db.commit()

    return {"message": "Marked as read"}

@router.patch("/{email_id}/unread")
def mark_unread(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if email.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    email.is_read = False
    db.commit()

    return {"message": "Marked as unread"}

@router.get("/inbox/count")
def inbox_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "inbox",
        Email.status == "delivered"
    ).count()

    return {"total": count}

@router.get("/search", response_model=list[EmailOut])
def search_emails(
    q: str,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Email).filter(
    Email.receiver_id == current_user.id,
    Email.folder == "inbox",
    Email.status == "delivered",
    or_(
        Email.subject.ilike(f"%{q}%"),
        Email.body.ilike(f"%{q}%")
    )
)