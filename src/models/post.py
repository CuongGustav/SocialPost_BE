from sqlalchemy import Column, Text, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from .base import Base
import uuid
import enum

class PostStatus(enum.Enum):
    valid = "valid"
    hidden = "hidden"
    deleted = "deleted"

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.valid)
    search_vector = Column(TSVECTOR)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")