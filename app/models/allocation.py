from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from app.database import Base


class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(Date, nullable=False)