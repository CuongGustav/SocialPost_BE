from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserSimpleResponse, UserResponse
from typing import List, Optional
from uuid import UUID
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

#Search user by text content
async def search_users(db: Session, search: Optional[str] = None) -> List[UserSimpleResponse]:
    query = db.query(User).filter(User.role == "user")
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.fullname.ilike(search_term))
        )
    
    users = query.with_entities(
        User.id,
        User.username,
        User.avatar_url,
        User.fullname
    ).all()
    
    result = [
        UserSimpleResponse(
            id=str(user.id),
            username=user.username,
            avatar_url=user.avatar_url,
            fullname=user.fullname
        )
        for user in users
    ]
    return result

#get info user by user_id
async def get_user_detail_by_user_id(db:Session, user_id:str) -> UserResponse:
    try:
        user_uuid = UUID(user_id) #convert str ->uuid

        user = db.query(User).filter(User.id == user_uuid).first()

        if not user:
            raise HTTPException (status_code=404, detail="user not found")
        
        return UserResponse.from_orm(user)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid user ID format")
