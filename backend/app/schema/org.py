from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime, time

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=200)
    legal_id: str = Field(..., max_length=100)
    zkp_threshold: float = Field(0.98, ge=0.0, le=1.0)
    is_active: int = 1

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    zkp_threshold: Optional[float] = None
    is_active: Optional[int] = None

class OrganizationResponse(OrganizationBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_deleted: int = 0

class DepartmentCreate(DepartmentBase):
    org_id: UUID4

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_deleted: Optional[int] = None

class DepartmentResponse(DepartmentBase):
    id: int
    org_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class ShiftBase(BaseModel):
    shift_name: str = Field(..., max_length=100)
    start_time: time
    end_time: time
    grace_period_mins: int = 5
    buffer_mins: int = 15
    break_deduct_mins: int = 0
    is_deleted: int = 0

class ShiftCreate(ShiftBase):
    org_id: UUID4

class ShiftUpdate(BaseModel):
    shift_name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    grace_period_mins: Optional[int] = None
    buffer_mins: Optional[int] = None
    break_deduct_mins: Optional[int] = None
    is_deleted: Optional[int] = None

class ShiftResponse(ShiftBase):
    id: int
    org_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True
