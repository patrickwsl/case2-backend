from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    read = "read"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
