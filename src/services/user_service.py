from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.user import User
from src.models.interaction import Interaction, InteractionType
from src.schemas.user import UserSimpleResponse, UserWithFollowResponse
from typing import List, Optional
from uuid import UUID
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Tìm kiếm người dùng theo nội dung văn bản
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

# Lấy thông tin chi tiết người dùng theo user_id
async def get_user_detail_by_user_id(db: Session, user_id: str) -> UserWithFollowResponse:
    try:
        # Xác thực và chuyển đổi user_id thành UUID
        user_uuid = UUID(user_id)
    except ValueError:
        logger.error(f"Định dạng UUID không hợp lệ cho user_id: {user_id}")
        raise HTTPException(status_code=400, detail="Định dạng ID người dùng không hợp lệ")

    user = (
        db.query(
            User,
            func.count(Interaction.id).label("follow_count")
        )
        .outerjoin(
            Interaction,
            (Interaction.target_user_id == User.id) &
            (Interaction.type == InteractionType.follow)
        )
        .filter(User.id == user_uuid)
        .group_by(User.id)
        .first()
    )

    if not user:
        logger.info(f"Không tìm thấy người dùng với user_id: {user_id}")
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user_obj, follow_count = user
    # Truyền follow_count vào from_orm
    response = UserWithFollowResponse.from_orm(
        user_obj,
        follow_count=follow_count if follow_count is not None else 0
    )

    return response