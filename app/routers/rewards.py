from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.services import lnbits

router = APIRouter()

@router.post("/rewards/withdraw")
async def withdraw_to_external(
    payment_request: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_invoice_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    balance_data = await lnbits.get_wallet_balance(x_api_key)
    balance_msats = balance_data.get("balance", 0)
    
    if balance_msats <= 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    result = await lnbits.pay_invoice(user.lnbits_admin_key, payment_request)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Payment failed: {result.get('error', 'Unknown error')}")
    
    return {
        "message": "Withdrawal successful",
        "amount_msats": result.get("amount", 0),
        "payment_hash": result.get("payment_hash", "")
    }

