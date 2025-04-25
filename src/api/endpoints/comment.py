# D:\workspace\SocialPost_BE\src\api\endpoints\comment.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.comment import CommentCreate, CommentWithUserResponse
from src.services.comment_service import create_comment as create_comment_service, get_comments_by_post_id
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["comments"])

async def get_current_user() -> str:
    return "fd61b848-fb84-4f23-9ff7-634da445f9ec"

# Add Comment
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    content: str = Form(...),
    post_id: str = Form(...),
    images: List[UploadFile] = File(None),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Received content: {content}, post_id: {post_id}, images: {images}")
    comment = CommentCreate(content=content, post_id=post_id)
    success = await create_comment_service(db, comment, images, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create comment"
        )
    return {"message": "Comment created successfully"}

#Get All Comment By Post Id
@router.get("/post/{post_id}", response_model=List[CommentWithUserResponse])
async def get_all_comments_by_post_id(post_id: str, db: Session = Depends(get_db)):
    comments = get_comments_by_post_id(db, post_id)
    return comments