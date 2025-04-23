from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.post import PostCreate, PostImageResponse, PostWithUserResponse
from src.services.post_service import create_post as create_post_service
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
async def get_all_posts(db: Session = Depends(get_db)):
    query = (
        select(
            Post,
            User.username,
            User.avatar_url,
            func.count(Interaction.id).filter(Interaction.type == "like").label("like_count"),
            func.count(Comment.id).label("comment_count"),
            func.count(Interaction.id).filter(Interaction.type == "share").label("share_count")
        )
        .join(User, Post.user_id == User.id)
        .outerjoin(Interaction, (Interaction.post_id == Post.id))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(Post.status == PostStatus.valid)
        .group_by(Post, User.username, User.avatar_url)
        .order_by(Post.created_at.desc())
    )
    posts = db.execute(query).all()

    result = []
    for post, username, avatar_url, like_count, comment_count, share_count in posts:
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
                like_count=like_count,
                comment_count=comment_count,
                share_count=share_count,
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat() if post.updated_at else None
            )
        )

    return result

@router.get("/search", response_model=List[PostWithUserResponse])
async def search_posts(
    query: str = Query(..., min_length=1, description="Search term for post content"),
    db: Session = Depends(get_db)
):
    tsquery = func.plainto_tsquery('simple', query)
    like_pattern = f"%{query}%"

    stmt = (
        select(
            Post,
            User.username,
            User.avatar_url,
            func.count(Interaction.id).filter(Interaction.type == "like").label("like_count"),
            func.count(Comment.id).label("comment_count"),
            func.count(Interaction.id).filter(Interaction.type == "share").label("share_count")
        )
        .join(User, Post.user_id == User.id)
        .outerjoin(Interaction, (Interaction.post_id == Post.id))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(Post.status == PostStatus.valid)
        .where(
            (Post.search_vector.op('@@')(tsquery)) | (Post.content.ilike(like_pattern))
        )
        .group_by(Post, User.username, User.avatar_url)
        .order_by(
            func.ts_rank(Post.search_vector, tsquery).desc(),
            Post.created_at.desc()
        )
    )
    posts = db.execute(stmt).all()

    result = []
    for post, username, avatar_url, like_count, comment_count, share_count in posts:
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
                like_count=like_count,
                comment_count=comment_count,
                share_count=share_count,
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat() if post.updated_at else None
            )
        )

    return result