from pydantic import BaseModel
from typing import Optional
from src.models.interaction import InteractionType

class InteractionCreate(BaseModel):
    type: InteractionType
    post_id: Optional[str] = None
    target_user_id: Optional[str] = None
    comment_id: Optional[str] = None