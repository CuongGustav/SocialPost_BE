from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.post import PostCreate, PostImageResponse, PostWithUserResponse
from src.services.post_service import create_post as create_post_service
from src.models.post import Post, PostStatus
from src.models.post_image import PostImage
from src.models.user import User
from sqlalchemy import select
from typing import List

router = APIRouter(prefix="/posts", tags=["posts"])


async def get_current_user() -> str:
    # Thay bằng logic xác thực JWT hoặc session thực tế
    return "4a8156d8-1a6c-41fc-a327-c106df1b89c8"  # ID của user Staff

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    content: str = Form(...),  # Nhận content từ form-data
    images: List[UploadFile] = File(None),  # Nhận danh sách ảnh, tùy chọn
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Tạo PostCreate từ content
    post = PostCreate(content=content)
    success = await create_post_service(db, post, images, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create post"
        )
    return {"message": "Post created successfully"}

@router.get("/", response_model=List[PostWithUserResponse])
async def get_all_posts(db: Session = Depends(get_db)):
    # Truy vấn lấy bài đăng, join với users
    query = (
        select(Post, User.username, User.avatar_url)
        .join(User, Post.user_id == User.id)
        .where(Post.status == PostStatus.valid)
    )
    posts = db.execute(query).all()

    # Tạo danh sách kết quả
    result = []
    for post, username, avatar_url in posts:
        # Lấy danh sách ảnh cho bài đăng
        images = db.query(PostImage).filter(PostImage.post_id == post.id).all()
        result.append(
            PostWithUserResponse(
                id=str(post.id),
                user_id=str(post.user_id),
                username=username,
                avatar_url=avatar_url,
                content=post.content,
                status=post.status,
                images=[
                    PostImageResponse(
                        id=str(image.id),
                        image_url=image.image_url,
                        created_at=image.created_at.isoformat()
                    )
                    for image in images
                ],
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat() if post.updated_at else None
            )
        )

    return result