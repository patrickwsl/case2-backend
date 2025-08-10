from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from app.database import Base


class DailyReturn(Base):
    __tablename__ = "daily_returns"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    date = Column(Date, nullable=False)
    close_price = Column(Float, nullable=False)