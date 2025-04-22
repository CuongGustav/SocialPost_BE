from sqlalchemy import Column, Text, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class NotificationType(enum.Enum):
    like = "like"
    comment = "comment"
    follow = "follow"
    message = "message"
    validation = "validation"

class NotificationStatus(enum.Enum):
    read = "read"
    unread = "unread"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.unread)
    content = Column(Text)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")