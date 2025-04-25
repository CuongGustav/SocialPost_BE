from sqlalchemy.orm import Session
from src.models.post import Post, PostStatus
from src.models.post_image import PostImage
from src.schemas.post import PostCreate, PostWithUserResponse, PostImageResponse
from fastapi import UploadFile, HTTPException
from sqlalchemy import select, func
from src.models.user import User
from src.models.interaction import Interaction
from src.models.comment import Comment
from typing import List
import uuid
import os
import logging

logger = logging.getLogger(__name__)

#create post
async def create_post(db: Session, post: PostCreate, images: List[UploadFile] | None, user_id: str):
    logger.info(f"Attempting to create post for user_id: {user_id}")

    db_post = Post(
        content=post.content,
        user_id=user_id,
        status=PostStatus.valid
    )
    db.add(db_post)
    db.commit()
    logger.info(f"Post created: {db_post.id}")

    if images:
        for image in images:
            if image.content_type not in ["image/jpeg", "image/png"]:
                logger.warning(f"Invalid image format: {image.content_type}")
                raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed")

            file_extension = image.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            image_path = os.path.join("static", "post", unique_filename)

            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            try:
                with open(image_path, "wb") as buffer:
                    content = await image.read()
                    buffer.write(content)
                image_url = f"/static/post/{unique_filename}"
                logger.info(f"Image saved: {image_url}")

                db_image = PostImage(
                    post_id=db_post.id,
                    image_url=image_url
                )
                db.add(db_image)
                logger.info(f"Image record created for post_id: {db_post.id}")
            except Exception as e:
                logger.error(f"Error saving image: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to save image")

        db.commit()

    return True

# get list post by content search
async def search_posts(db: Session, query: str) -> List[PostWithUserResponse]:
    logger.info(f"Searching posts with query: {query}")
    
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

    logger.info(f"Found {len(result)} posts matching query: {query}")
    return result

#get all post
async def get_all_posts(db: Session) -> List[PostWithUserResponse]:
    logger.info("Fetching all valid posts")
    
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

    logger.info(f"Retrieved {len(result)} posts")
    return result

#get all post by user_id
async def get_posts_by_user_id (db: Session, user_id: str) -> List[PostWithUserResponse]:

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
            .where(Post.user_id == user_id)
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
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
#get post by post id
async def get_post_by_post_id(db: Session, post_id: str) -> PostWithUserResponse: 
    logger.info(f"Fetching post with post_id: {post_id}")

    try:
        post_check = db.query(Post).filter(Post.id == post_id).first()
        if not post_check:
            logger.warning(f"Post not found: {post_id}")
            raise HTTPException(status_code=404, detail="Post not found")

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
            .outerjoin(Interaction, Interaction.post_id == Post.id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .where(Post.id == post_id)
            .where(Post.status == PostStatus.valid)
            .group_by(Post, User.username, User.avatar_url)
        )

        result = db.execute(query).first()

        if not result:
            logger.warning(f"Post not found or invalid: {post_id}")
            raise HTTPException(status_code=404, detail="Post not found or not valid")

        post, username, avatar_url, like_count, comment_count, share_count = result

        images = db.query(PostImage).filter(PostImage.post_id == post.id).all()

        post_response = PostWithUserResponse(
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

        logger.info(f"Successfully fetched post with post_id: {post_id}")
        return post_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching post with post_id {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")