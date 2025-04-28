from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.schemas.violation import ViolationCreate, ViolationResponse
from src.services.violation_service import create_violation, get_violations_by_user_id
from typing import List

router = APIRouter(
    prefix="/violations",
    tags=["violations"],
)

@router.post("/", response_model=ViolationResponse)
async def add_violation(violation: ViolationCreate, db: Session = Depends(get_db)):
    return await create_violation(db, violation)

@router.get("/user/{user_id}", response_model=List[ViolationResponse])
async def get_all_violaion_by_user_id(user_id: str, db:Session =Depends(get_db)):
    return await get_violations_by_user_id(db, user_id)