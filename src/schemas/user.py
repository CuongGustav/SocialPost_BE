from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from src.models.user import UserStatus, UserRole
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    fullname: Optional[str] = None  

    @field_validator("username")
    def username_length(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Tên người dùng phải từ 3 đến 50 ký tự")
        return v

    @field_validator("password")
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v

    @field_validator("fullname")
    def fullname_length(cls, v):
        if v and len(v) > 255:
            raise ValueError("Tên đầy đủ không được vượt quá 255 ký tự")
        return v

class UserWithFollowResponse(BaseModel):
    id: str
    username: str
    avatar_url: Optional[str] = None
    fullname: Optional[str] = None  
    bio: Optional[str] = None
    follow_count: int
    status: UserStatus
    created_at: str

    @classmethod
    def from_orm(cls, obj, follow_count: int = 0):
        return cls(
            id=str(obj.id),
            username=obj.username,
            avatar_url=obj.avatar_url,
            fullname=obj.fullname,  
            bio=obj.bio,
            status=obj.status,
            created_at=obj.created_at.isoformat() if obj.created_at else None,
            follow_count=follow_count
        )

    class Config:
        from_attributes = True

class UserSimpleResponse(BaseModel):
    id: str
    username: str
    avatar_url: Optional[str]
    fullname: Optional[str]

    class Config:
        from_attributes = True