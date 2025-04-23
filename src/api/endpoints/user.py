from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.utils.database import get_db
from src.models.user import User
from src.schemas.user import UserResponse, UserSimpleResponse
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=List[UserSimpleResponse])
async def get_all_user_by_text(
    search: Optional[str] = Query(None, description="Search term for username or fullname"),
    db: Session = Depends(get_db)
):
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
    
    return [
        UserSimpleResponse(
            id=str(user.id),
            username=user.username,
            avatar_url=user.avatar_url,
            fullname=user.fullname
        )
        for user in users
    ]