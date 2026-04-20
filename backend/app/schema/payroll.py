from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class PayrollBase(BaseModel):
    month: int
    year: int

class PayrollCreate(PayrollBase):
    user_id: int
    base_salary: float
    deductions: float = 0.0
    reimbursements_total: float = 0.0
    total_salary: float

class PayrollUpdate(BaseModel):
    status: str

class PayrollResponse(PayrollBase):
    id: int
    user_id: int
    org_id: uuid.UUID
    base_salary: float
    deductions: float
    reimbursements_total: float
    total_salary: float
    status: str
    generated_at: datetime

    class Config:
        from_attributes = True
