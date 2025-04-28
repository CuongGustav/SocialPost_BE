from pydantic import BaseModel, UUID4
from enum import Enum
from datetime import datetime

class ViolationTargetType(str, Enum):
    post = "post"
    comment = "comment"

class ViolationCreate(BaseModel):
    user_id: UUID4
    target_type: ViolationTargetType
    reason: str

class ViolationResponse(BaseModel):
    id: UUID4
    target_type: ViolationTargetType
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True