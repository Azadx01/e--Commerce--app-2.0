from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "customer" # Can be strictly validated later

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    status: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    role: Optional[str] = None
