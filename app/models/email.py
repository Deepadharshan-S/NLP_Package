from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_emails")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_emails")

    subject = Column(String)
    body = Column(Text)
    is_read = Column(Boolean, default=False)

    is_spam = Column(Boolean, default=False)
    status = Column(String, default="pending")  

    folder = Column(String, default="pending")

    timestamp = Column(DateTime, default=datetime.utcnow)