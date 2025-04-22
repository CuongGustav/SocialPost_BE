from sqlalchemy import Column, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class InteractionType(enum.Enum):
    like = "like"
    follow = "follow"
    report = "report"
    report_comment = "report_comment"

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    type = Column(Enum(InteractionType), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))