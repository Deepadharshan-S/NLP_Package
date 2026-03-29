from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    sent_emails = relationship("Email", foreign_keys="Email.sender_id", back_populates="sender")
    received_emails = relationship("Email", foreign_keys="Email.receiver_id", back_populates="receiver")