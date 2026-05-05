
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    confirm_password: str

class PasswordResetToken(BaseModel):
    token: str
    expires_at: datetime
    email: EmailStr

