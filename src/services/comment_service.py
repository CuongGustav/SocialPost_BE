from sqlalchemy.orm import Session
from src.models.comment import Comment, CommentStatus
from src.models.comment_image import CommentImage
from src.schemas.comment import CommentCreate, CommentImageResponse, CommentStatus, CommentWithUserResponse
from fastapi import UploadFile, HTTPException
from typing import List
from src.models.post import Post, PostStatus
from src.models.user import User
import uuid
import os
import logging

logger = logging.getLogger(__name__)

#Create Comment
async def create_comment(db: Session, comment:CommentCreate, images: List[UploadFile] | None, user_id:str):

    post = db.query(Post).filter(Post.id == comment.post_id, Post.status == PostStatus.valid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or not valid")
    
    db_comment = Comment(
        content = comment.content,
        post_id = comment.post_id,
        user_id = user_id,
        status = CommentStatus.valid
    )
    db.add(db_comment)
    db.commit()

    if images:
        for image in images:
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed")
            
            file_extension = image.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            image_path = os.path.join("static", "comment", unique_filename)

            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            try:
                with open(image_path, "wb") as buffer:
                    content = await image.read()
                    buffer.write(content)
                image_url = f"/static/comment/{unique_filename}"

                db_image = CommentImage(
                    comment_id=db_comment.id,
                    image_url=image_url
                )
                db.add(db_image)
            except Exception as e:
                raise HTTPException(status_code=500, detail="Failed to save image")

        db.commit()

    return True

#Get All Comment By Post Id
def get_comments_by_post_id(db: Session, post_id: str) -> List[CommentWithUserResponse]:
    logger.info(f"Fetching comments for post_id: {post_id}")

    # Kiểm tra bài viết có tồn tại và ở trạng thái valid
    post = db.query(Post).filter(Post.id == post_id, Post.status == PostStatus.valid).first()
    if not post:
        logger.warning(f"Post not found or invalid: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found or not valid")

    # Truy vấn các bình luận, join với bảng User và CommentImage
    comments = (
        db.query(Comment, User.username, User.avatar_url)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.post_id == post_id, Comment.status == CommentStatus.valid)
        .all()
    )

    result = []
    for comment, username, avatar_url in comments:
        images = db.query(CommentImage).filter(CommentImage.comment_id == comment.id).all()

        comment_response = CommentWithUserResponse(
            id=str(comment.id),
            post_id=str(comment.post_id),
            user_id=str(comment.user_id),
            username=username,
            avatar_url=avatar_url,
            content=comment.content,
            status=comment.status,
            images=[
                CommentImageResponse(
                    id=str(image.id),  
                    image_url=image.image_url,
                    created_at=str(image.created_at) 
                ) for image in images
            ],
            created_at=str(comment.created_at),
            updated_at=str(comment.updated_at) if comment.updated_at else None
        )
        result.append(comment_response)

    logger.info(f"Found {len(result)} comments for post_id: {post_id}")
    return result