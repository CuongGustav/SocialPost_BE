from pydantic import BaseModel
from src.models.comment import CommentStatus
from typing import List, Optional

#Tạo bình luận
class CommentCreate (BaseModel):
    content: str
    post_id: str

#Trả về một bình luận
class CommentResponse (BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    status: CommentStatus
    create_at: str
    updated_at: Optional[str]

    #Cho phép chuyển đổi tự động từ các mô hình ORM sang Pydantic model
    class Config:
        from_attributes = True

#Trả hình ảnh đính kèm với bình luận
class CommentImageResponse(BaseModel):
    id: str
    image_url: str
    created_at: str

    class Config:
        from_attributes = True

class CommentWithUserResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    username: str
    avatar_url: Optional[str]
    content: str
    status: CommentStatus
    images: List[CommentImageResponse]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True
