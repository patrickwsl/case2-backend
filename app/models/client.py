from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base

class ClientStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(Enum(ClientStatus), default=ClientStatus.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
