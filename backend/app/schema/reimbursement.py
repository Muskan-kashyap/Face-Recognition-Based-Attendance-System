from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class ReimbursementBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    reason: str = Field(..., min_length=1, max_length=500)
    receipt_url: Optional[str] = Field(None, max_length=512)
    category: Optional[str] = Field("other", pattern="^(travel|meals|supplies|other)$")

class ReimbursementCreate(ReimbursementBase):
    pass

class ReimbursementUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected|paid)$")
    processed_at: Optional[datetime] = None

class ReimbursementResponse(ReimbursementBase):
    id: int
    user_id: int
    org_id: uuid.UUID
    status: str
    submitted_at: datetime
    processed_at: Optional[datetime]
    approved_by: Optional[int]

    class Config:
        from_attributes = True
