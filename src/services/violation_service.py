from sqlalchemy.orm import Session
from ..models.violation import Violation, ViolationTargetType
from ..models.user import User, UserStatus
from ..schemas.violation import ViolationCreate, ViolationResponse
from fastapi import HTTPException
from typing import List

#create violation
def create_violation(db: Session, violation: ViolationCreate) -> ViolationResponse:

    try:
        user = db.query(User).filter(User.id == violation.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db_violation = Violation(
            user_id=violation.user_id,
            target_type=violation.target_type,
            reason=violation.reason
        )
        db.add(db_violation)

        user.violation_count += 1

        if user.violation_count >= 14:
            user.status = UserStatus.banned

        db.commit()
        db.refresh(db_violation)
        return ViolationResponse.model_validate(db_violation)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating violation: {str(e)}")


#get all violation by user id
async def get_violations_by_user_id (db:Session, user_id: str) -> List[ViolationResponse]:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        violations = db.query(Violation).filter(Violation.user_id == user_id).all()
        return [ViolationResponse.model_validate(violation) for violation in violations]
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving violations: {str(e)}")
