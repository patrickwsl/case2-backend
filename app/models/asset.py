from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    name = Column(String, nullable=False)

    allocations = relationship("Allocation", back_populates="asset")