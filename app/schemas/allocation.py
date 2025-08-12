from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class AllocationBase(BaseModel):
    client_id: int
    asset_id: int
    quantity: float
    buy_price: Optional[float] = None
    buy_date: Optional[date] = None
    is_active: Optional[bool] = True


class AllocationCreate(AllocationBase):
    pass


class AllocationUpdate(BaseModel):
    quantity: Optional[float] = None
    buy_price: Optional[float] = None
    buy_date: Optional[date] = None


class AllocationResponse(AllocationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
