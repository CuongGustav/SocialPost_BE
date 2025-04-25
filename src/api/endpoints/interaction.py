from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.interaction import InteractionCreate
from src.services.interaction_service import create_interaction
from typing import Optional

router = APIRouter(prefix="/interactions", tags=["interactions"])

async def get_current_user() -> str:
    # Thay bằng logic xác thực JWT hoặc session thực tế
    return "fd61b848-fb84-4f23-9ff7-634da445f9ec"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_interaction_endpoint(
    interaction: InteractionCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = await create_interaction(
        db,
        user_id,
        interaction.type,
        post_id=interaction.post_id,
        target_user_id=interaction.target_user_id,
        comment_id=interaction.comment_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create interaction"
        )
    return {"message": "Interaction created successfully"}