from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from datetime import datetime
from app.db.base import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))

    subject = Column(String)
    body = Column(Text)
    is_read = Column(Boolean, default=False)

    is_spam = Column(Boolean, default=False)
    status = Column(String, default="pending")  

    folder = Column(String, default="pending")

    timestamp = Column(DateTime, default=datetime.utcnow)