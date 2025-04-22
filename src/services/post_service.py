from sqlalchemy.orm import Session
from src.models.post import Post, PostStatus
from src.models.post_image import PostImage
from src.schemas.post import PostCreate
from fastapi import UploadFile, HTTPException
from typing import List
import uuid
import os
import logging

# Thiết lập logging
logger = logging.getLogger(__name__)

async def create_post(db: Session, post: PostCreate, images: List[UploadFile] | None, user_id: str):
    logger.info(f"Attempting to create post for user_id: {user_id}")

    # Tạo bài đăng
    db_post = Post(
        content=post.content,
        user_id=user_id,
        status=PostStatus.valid
    )
    db.add(db_post)
    db.commit()
    logger.info(f"Post created: {db_post.id}")

    # Xử lý danh sách ảnh
    if images:
        for image in images:
            # Kiểm tra định dạng ảnh
            if image.content_type not in ["image/jpeg", "image/png"]:
                logger.warning(f"Invalid image format: {image.content_type}")
                raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed")

            # Tạo tên file duy nhất bằng UUID
            file_extension = image.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            image_path = os.path.join("static", "post", unique_filename)

            # Tạo thư mục static/post nếu chưa tồn tại
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            # Lưu ảnh
            try:
                with open(image_path, "wb") as buffer:
                    content = await image.read()
                    buffer.write(content)
                image_url = f"/static/post/{unique_filename}"
                logger.info(f"Image saved: {image_url}")

                # Lưu vào bảng post_images
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