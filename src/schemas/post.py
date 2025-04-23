from pydantic import BaseModel
from src.models.post import PostStatus
from typing import List, Optional

class PostCreate(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: str
    user_id: str
    content: str
    status: PostStatus
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class PostImageResponse(BaseModel):
    id: str
    image_url: str
    created_at: str

    class Config:
        from_attributes = True

class PostWithUserResponse(BaseModel):
    id: str
    user_id: str
    username: str
    avatar_url: Optional[str]
    content: str
    status: PostStatus
    images: List[PostImageResponse]
    like_count: int  
    comment_count: int  
    share_count: int  
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True