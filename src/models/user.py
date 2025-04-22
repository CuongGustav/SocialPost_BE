from sqlalchemy import Column, String, Enum, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class UserStatus(enum.Enum):
    active = "active"
    banned = "banned"

class UserRole(enum.Enum):
    user = "user"
    staff = "staff"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(255))
    bio = Column(Text)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")