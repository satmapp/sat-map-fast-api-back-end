from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.services import lnbits

router = APIRouter()

@router.post("/rewards/withdraw")
async def withdraw_rewards(user_id: int, payment_request: str, db: Session = Depends(get_db)):
    balance = crud.get_user_balance(db, user_id)
    if balance <= 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    result = await lnbits.pay_invoice(payment_request)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail="Payment failed")
    
    user = crud.get_user(db, user_id)
    user.sats_earned = 0
    db.commit()
    
    return {"message": "Withdrawal successful", "amount": balance}

