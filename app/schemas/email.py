from pydantic import BaseModel
from fastapi import Form
from datetime import datetime


class EmailCreate(BaseModel):
    receiver_email: str
    subject: str
    body: str
    @classmethod
    def as_form(
        cls,
        receiver_email: str = Form(...),
        subject: str = Form(...),
        body: str = Form(...)
    ):
        return cls(
            receiver_email=receiver_email,
            subject=subject,
            body=body
        )


class EmailOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    subject: str
    body: str
    is_spam: bool
    status: str
    folder: str
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True