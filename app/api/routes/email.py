import os

from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import BackgroundTasks
from app.services.email_service import process_email
from app.schemas.email import EmailCreate, EmailOut
from app.models.email import Email
from app.api.deps import get_db, get_current_user
from app.models.user import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../../templates"))

router = APIRouter(prefix="/emails", tags=["Emails"])

@router.post("/send")  
def send_email(
    receiver_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    email = EmailCreate(
        receiver_email=receiver_email,
        subject=subject,
        body=body
    )

    receiver = db.query(User).filter(
        User.email == email.receiver_email.lower().strip()
    ).first()

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if receiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send email to yourself")

    new_email = Email(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        subject=email.subject,
        body=email.body,
        status="pending",
        folder="pending"
    )

    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    background_tasks.add_task(process_email, new_email.id)

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/inbox", status_code=303)

@router.get("/inbox", response_model=list[EmailOut])
def get_inbox(
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    emails = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "inbox",
        Email.status == "delivered"
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()
    
    return emails

@router.get("/list")
def email_list(
    request: Request,
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emails = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "inbox",
        Email.status == "delivered"
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()   # ✅ FIX

    total = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "inbox",  
        Email.status == "delivered"
    ).count()

    return templates.TemplateResponse(
        request,
        "email_list.html",
        {
            "emails": emails,
            "offset": offset,
            "limit": limit,
            "total": total,
            "route": "/emails/list"
        }
    )
    
@router.get("/spam/list")
def spam_list(
    request: Request,
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emails = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "spam",
        Email.status == "delivered"
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()

    total = db.query(Email).filter(
        Email.receiver_id == current_user.id,
        Email.folder == "spam",
        Email.status == "delivered"
    ).count()

    return templates.TemplateResponse(
    request,
    "email_list.html",
    {
        "emails": emails,
        "offset": offset,
        "limit": limit,
        "total": total,
        "route": "/emails/spam/list"   # 🔥 ADD THIS
    }
)
    
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
    
@router.get("/detail/{email_id}", response_model=EmailOut)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(
    Email.id == email_id,
    Email.status == "delivered"
).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if email.sender_id != current_user.id and email.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 📖 Auto mark as read (only for receiver)
    if email.receiver_id == current_user.id:
        email.is_read = True
        db.commit()

    return email

@router.patch("/detail/{email_id}/read")
def mark_read(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(Email.id == email_id,Email.status == "delivered").first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if email.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    email.is_read = True
    db.commit()

    return {"message": "Marked as read"}

@router.patch("/detail/{email_id}/unread")
def mark_unread(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = db.query(Email).filter(Email.id == email_id,Email.status == "delivered").first()

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
    ).order_by(Email.timestamp.desc()).offset(offset).limit(limit).all()
    

@router.get("/view/{email_id:int}")
def email_view(
    email_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = db.query(Email).options(
            joinedload(Email.sender)
        ).filter(
            Email.id == email_id
        ).first()

    if not email:
        return templates.TemplateResponse(
            request,
            "email_view.html",
            {"email": None}
        )

    if email.receiver_id == current_user.id:
        email.is_read = True
        db.commit()

    return templates.TemplateResponse(
        request,
        "email_view.html",
        {"email": email}
    )