from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    asset = relationship("Asset", back_populates="allocations")
