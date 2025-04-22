from sqlalchemy import Column, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class GroupRole(enum.Enum):
    admin = "admin"
    member = "member"

class GroupMember(Base):
    __tablename__ = "group_members"

    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(GroupRole), nullable=False, default=GroupRole.member)
    joined_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")