from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.utils.database import get_db
from src.models.user import User
from src.schemas.user import UserResponse, UserSimpleResponse
from src.services.user_service import search_users
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=List[UserSimpleResponse])
async def search_users_endpoint(
    search: Optional[str] = Query(None, description="Search term for username or fullname"),
    db: Session = Depends(get_db)
):
    return await search_users(db, search)