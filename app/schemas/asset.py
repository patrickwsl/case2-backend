from pydantic import BaseModel


class AssetBase(BaseModel):
    id: int
    ticker: str
    name: str

