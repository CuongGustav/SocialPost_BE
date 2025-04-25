from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserSimpleResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

async def search_users(db: Session, search: Optional[str] = None) -> List[UserSimpleResponse]:
    logger.info(f"Searching users with search term: {search or 'None'}")
    
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
    
    logger.info(f"Found {len(result)} users matching search term: {search or 'None'}")
    return result