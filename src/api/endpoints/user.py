from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.utils.database import get_db
from src.models.user import User
from src.schemas.user import UserResponse, UserSimpleResponse
from src.services.user_service import search_users, get_user_detail_by_user_id
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

#Search user by context
@router.get("/search", response_model=List[UserSimpleResponse])
async def search_users_endpoint(
    search: Optional[str] = Query(None, description="Search term for username or fullname"),
    db: Session = Depends(get_db)
):
    return await search_users(db, search)

#Get user by id
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail_endpoint(
    user_id:str,
    db: Session = Depends(get_db)
):
    return await get_user_detail_by_user_id(db, user_id)