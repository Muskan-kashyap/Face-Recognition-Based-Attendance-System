from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

class TicketBase(BaseModel):
    title: str
    description: str
    priority: str = "medium"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

class TicketResponse(TicketBase):
    id: int
    user_id: int
    org_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
