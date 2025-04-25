from sqlalchemy.orm import Session
from src.models.interaction import Interaction, InteractionType
from src.models.user import User
from src.models.post import Post, PostStatus
from src.models.comment import Comment
from fastapi import HTTPException
import logging
from typing import Optional
import uuid

logger = logging.getLogger(__name__)

async def create_interaction(
    db: Session,
    user_id: str,
    interaction_type: InteractionType,
    post_id: Optional[str] = None,
    target_user_id: Optional[str] = None,
    comment_id: Optional[str] = None
) -> bool:
    logger.info(f"Creating interaction for user_id: {user_id}, type: {interaction_type}, post_id: {post_id}, target_user_id: {target_user_id}, comment_id: {comment_id}")

    try:
        # Check the user exists and not banned
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        if user.status == "banned":
            logger.warning(f"User is banned: {user_id}")
            raise HTTPException(status_code=403, detail="User is banned")

        # Validate UUID format for post_id, target_user_id, comment_id if provided
        if post_id:
            try:
                uuid.UUID(post_id)
            except ValueError:
                logger.warning(f"Invalid post_id format: {post_id}")
                raise HTTPException(status_code=400, detail="Invalid post_id format")
        if target_user_id:
            try:
                uuid.UUID(target_user_id)
            except ValueError:
                logger.warning(f"Invalid target_user_id format: {target_user_id}")
                raise HTTPException(status_code=400, detail="Invalid target_user_id format")
        if comment_id:
            try:
                uuid.UUID(comment_id)
            except ValueError:
                logger.warning(f"Invalid comment_id format: {comment_id}")
                raise HTTPException(status_code=400, detail="Invalid comment_id format")

        # Check input data based on interactive type
        if interaction_type == InteractionType.like:
            if not post_id:
                logger.warning("Post ID required for like interaction")
                raise HTTPException(status_code=400, detail="Post ID is required for like")
            post = db.query(Post).filter(Post.id == post_id, Post.status == PostStatus.valid).first()
            if not post:
                logger.warning(f"Valid post not found: {post_id}")
                raise HTTPException(status_code=404, detail="Post not found or not valid")
            
        elif interaction_type == InteractionType.share:
            if not post_id:
                logger.warning("Post ID required for share interaction")
                raise HTTPException(status_code=400, detail="Post ID is required for share")
            if target_user_id:
                logger.info(f"Ignoring target_user_id {target_user_id} for share interaction")
                target_user_id = None  
            if comment_id:
                logger.info(f"Ignoring comment_id {comment_id} for share interaction")
                comment_id = None  
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                logger.warning(f"Post not found: {post_id}")
                raise HTTPException(status_code=404, detail="Post not found")
            
        elif interaction_type == InteractionType.follow:
            if not target_user_id:
                logger.warning("Target user ID required for follow interaction")
                raise HTTPException(status_code=400, detail="Target user ID is required for follow")
            target_user = db.query(User).filter(User.id == target_user_id).first()
            if not target_user:
                logger.warning(f"Target user not found: {target_user_id}")
                raise HTTPException(status_code=404, detail="Target user not found")
            if target_user_id == user_id:
                logger.warning(f"User cannot follow themselves: {user_id}")
                raise HTTPException(status_code=400, detail="Cannot follow yourself")

        elif interaction_type == InteractionType.report:
            if not post_id:
                logger.warning("Post ID required for report interaction")
                raise HTTPException(status_code=400, detail="Post ID is required for report")
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                logger.warning(f"Post not found: {post_id}")
                raise HTTPException(status_code=404, detail="Post not found")

        elif interaction_type == InteractionType.report_comment:
            if not comment_id:
                logger.warning("Comment ID required for report_comment interaction")
                raise HTTPException(status_code=400, detail="Comment ID is required for report_comment")
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                logger.warning(f"Comment not found: {comment_id}")
                raise HTTPException(status_code=404, detail="Comment not found")

        # Check duplicated interaction
        existing_interaction = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.type == interaction_type,
            Interaction.post_id == post_id,
            (Interaction.target_user_id == target_user_id) | (Interaction.target_user_id.is_(None) & (target_user_id is None)),
            (Interaction.comment_id == comment_id) | (Interaction.comment_id.is_(None) & (comment_id is None))
        ).first()
        if existing_interaction:
            logger.warning(f"Duplicate interaction found: user_id={user_id}, type={interaction_type}, post_id={post_id}")
            raise HTTPException(status_code=400, detail=f"Interaction already exists")

        # Create new interaction
        db_interaction = Interaction(
            user_id=user_id,
            type=interaction_type,
            post_id=post_id,
            target_user_id=target_user_id,
            comment_id=comment_id
        )
        db.add(db_interaction)
        db.commit()
        logger.info(f"Interaction created: id={db_interaction.id}, type={interaction_type}")

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating interaction for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")