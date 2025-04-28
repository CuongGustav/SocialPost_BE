from sqlalchemy import Column, TIMESTAMP, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class ViolationTargetType(enum.Enum):
    post = "post"
    comment = "comment"

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_type = Column(Enum(ViolationTargetType), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default="CURRENT_TIMESTAMP")
    reason = Column(Text, nullable=False)