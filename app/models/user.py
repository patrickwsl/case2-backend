from sqlalchemy import Column, Integer, String, Enum
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    read = "read"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.read, nullable=False)
