from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from src.utils.database import get_db
from src.models.user import User
from src.schemas.user import UserWithFollowResponse, UserSimpleResponse
from src.services.user_service import search_users, get_user_detail_by_user_id
from typing import List
from pydantic import UUID4

router = APIRouter(prefix="/users", tags=["users"])

# Tìm kiếm người dùng theo nội dung
@router.get("/search", response_model=List[UserSimpleResponse])
async def search_users_endpoint(
    search: Optional[str] = Query(None, description="Từ khóa tìm kiếm cho tên người dùng hoặc tên đầy đủ"),
    db: Session = Depends(get_db)
):
    return await search_users(db, search)

# Lấy chi tiết người dùng theo user_id
@router.get("/{user_id}", response_model=UserWithFollowResponse)
async def get_user_detail_endpoint(
    user_id: UUID4 = Path(..., description="UUID của người dùng"),
    db: Session = Depends(get_db)
):
    return await get_user_detail_by_user_id(db, str(user_id))