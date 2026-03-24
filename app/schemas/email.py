from pydantic import BaseModel
from datetime import datetime


class EmailCreate(BaseModel):
    receiver_id: int
    subject: str
    body: str


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