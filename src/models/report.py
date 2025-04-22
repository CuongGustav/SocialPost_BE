from sqlalchemy import Column, Text, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
import enum

class ReportStatus(enum.Enum):
    open = "open"
    closed = "closed"

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.open)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    handled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    handled_at = Column(TIMESTAMP)