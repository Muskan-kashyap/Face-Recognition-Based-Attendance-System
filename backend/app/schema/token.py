from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    jti: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None
    permissions: Optional[list[str]] = []
