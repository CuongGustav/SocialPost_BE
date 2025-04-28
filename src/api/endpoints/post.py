from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.post import PostCreate, PostImageResponse, PostWithUserResponse
from src.services.post_service import (create_post as create_post_service, search_posts, get_all_posts, get_posts_by_user_id, 
                                       get_post_by_post_id, get_shared_posts_by_user_id)
from src.models.post import Post, PostStatus
from src.models.post_image import PostImage
from src.models.user import User
from src.models.interaction import Interaction
from src.models.comment import Comment
from sqlalchemy import select, func
from typing import List

router = APIRouter(prefix="/posts", tags=["posts"])

async def get_current_user() -> str:
    # Thay bằng logic xác thực JWT hoặc session thực tế
    return "fd61b848-fb84-4f23-9ff7-634da445f9ec"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    content: str = Form(...),
    images: List[UploadFile] = File(None),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = PostCreate(content=content)
    success = await create_post_service(db, post, images, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create post"
        )
    return {"message": "Post created successfully"}

@router.get("/", response_model=List[PostWithUserResponse])
async def get_all_posts_endpoint(db: Session = Depends(get_db)):
    return await get_all_posts(db)

@router.get("/search", response_model=List[PostWithUserResponse])
async def search_posts_endpoint(
    query: str = Query(..., min_length=1, description="Search term for post content"),
    db: Session = Depends(get_db)
):
    return await search_posts(db, query)

@router.get("/user/{user_id}", response_model=List[PostWithUserResponse])
async def get_posts_by_user_id_endpoint(
    user_id: str,
    db: Session = Depends(get_db)
):
    return await get_posts_by_user_id(db, user_id)

@router.get("/postshare/user/{user_id}", response_model=List[PostWithUserResponse])
async def get_share_posts_by_user_id_endpoint(
    user_id: str,
    db:Session =Depends(get_db)
):
    return await get_shared_posts_by_user_id(db, user_id)

@router.get("/{post_id}", response_model=PostWithUserResponse)
async def get_post_by_post_id_endpoint(post_id: str, db: Session = Depends(get_db)):
    return await get_post_by_post_id(db, post_id)