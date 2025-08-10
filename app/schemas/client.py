from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class ClientBase(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    status: StatusEnum = StatusEnum.active

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    status: StatusEnum | None = None

class ClientOut(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
