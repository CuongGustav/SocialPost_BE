from sqlalchemy.orm import Session
from src.models.user import User, UserStatus, UserRole
from src.schemas.user import UserCreate
from src.utils.auth import hash_password
import logging

logger = logging.getLogger(__name__)

async def create_user(db: Session, user: UserCreate):
    logger.info(f"Attempting to create user: {user.username}, {user.email}")
    
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        logger.warning(f"User already exists: {user.username}, {user.email}")
        return False

    hashed_password = hash_password(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        status=UserStatus.active,
        role=UserRole.user
    )

    db.add(db_user)
    db.commit()
    logger.info(f"User created: {db_user.id}")
    return True