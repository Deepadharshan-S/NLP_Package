from app.db.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from app.core.security import hash_password
from datetime import datetime
import random

db = SessionLocal()

# -----------------------
# 👤 Create Users
# -----------------------
users_data = [
    "alice@gmail.com",
    "bob@gmail.com",
    "charlie@gmail.com",
    "david@gmail.com"
]

users = []

for email in users_data:
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            email=email,
            password_hash=hash_password("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        users.append(user)
    else:
        users.append(existing)

print("Users created")

# -----------------------
# 📧 Create Emails
# -----------------------
subjects = [
    "Meeting Reminder",
    "Project Update",
    "Urgent: Check this",
    "Hello!",
    "Important Notice",
    "Weekend Plans"
]

bodies = [
    "Let's meet tomorrow at 10 AM.",
    "Project is going well.",
    "Please check ASAP.",
    "Hope you're doing well.",
    "This is important.",
    "What are your plans?"
]

for _ in range(50):  # create 30 emails
    sender = random.choice(users)
    receiver = random.choice(users)

    if sender.id == receiver.id:
        continue

    email = Email(
        sender_id=sender.id,
        receiver_id=receiver.id,
        subject=random.choice(subjects),
        body=random.choice(bodies),
        status="delivered",
        folder="inbox",
        is_read=random.choice([True, False]),
        timestamp=datetime.utcnow()
    )

    db.add(email)

db.commit()
print("Emails created")

db.close()