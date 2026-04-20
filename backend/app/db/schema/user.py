from pydantic import EmailStr, BaseModel
from typing import Union

class UserinCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserinUpdate(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    email: Union[EmailStr, None] = None
    password: Union[str, None] = None

class UserinLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserwithToken(BaseModel):
    user: UserOutput
    token: str