from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from src.models.user import UserStatus, UserRole
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    def username_length(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return v

    @field_validator("password")
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    status: UserStatus
    role: UserRole
    created_at: str
    updated_at: Optional[str] = None  

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            username=obj.username,
            email=obj.email,
            avatar_url=obj.avatar_url,
            bio=obj.bio,
            status=obj.status,
            role=obj.role,
            created_at=obj.created_at.isoformat() if obj.created_at else None,
            updated_at=obj.updated_at.isoformat() if obj.updated_at else None
        )

    class Config:
        from_attributes = True