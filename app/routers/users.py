from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.post("/users", response_model=schemas.User)
def create_user(wallet_id: str, db: Session = Depends(get_db)):
    existing = crud.get_user_by_wallet(db, wallet_id)
    if existing:
        return existing
    return crud.create_user(db, wallet_id)

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{user_id}/balance")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    balance = crud.get_user_balance(db, user_id)
    return {"user_id": user_id, "balance_sats": balance}

