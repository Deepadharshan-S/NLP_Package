from app.db.database import SessionLocal
from app.models.email import Email
from app.services.spam import predict_spam

def process_email(email_id: int):
    db = SessionLocal()

    try:
        email = db.query(Email).filter(Email.id == email_id).first()

        if not email:
            return

        email.status = "processing"
        db.commit()

        # 🤖 spam check
        is_spam, _ = predict_spam(email.body)

        email.is_spam = is_spam
        email.folder = "spam" if is_spam else "inbox"
        email.status = "delivered"

        db.commit()

    finally:
        db.close()