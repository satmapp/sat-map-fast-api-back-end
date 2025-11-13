from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.services import lnbits

router = APIRouter()

@router.post("/users/register", response_model=schemas.UserWithKeys)
async def register_user(username: str, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    wallet_data = await lnbits.create_user_wallet(username)
    
    if "error" in wallet_data:
        raise HTTPException(status_code=500, detail=f"Failed to create wallet: {wallet_data.get('error')}")
    
    wallets = wallet_data.get("wallets", [])
    if not wallets or not wallets[0]:
        raise HTTPException(status_code=500, detail="LNbits wallet creation failed - empty response")
    
    wallet = wallets[0]
    
    lnbits_invoice_key = wallet.get("inkey")
    lnbits_admin_key = wallet.get("adminkey")
    lnbits_wallet_id = wallet.get("id")
    
    if not lnbits_invoice_key or not lnbits_admin_key or not lnbits_wallet_id:
        raise HTTPException(status_code=500, detail=f"LNbits returned incomplete wallet data: {wallet_data}")
    
    user = crud.create_user_with_wallet(
        db,
        username=username,
        lnbits_user_id=None,
        lnbits_wallet_id=lnbits_wallet_id,
        lnbits_admin_key=lnbits_admin_key,
        lnbits_invoice_key=lnbits_invoice_key
    )
    
    return user

@router.get("/users/me", response_model=schemas.User)
async def get_current_user(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_invoice_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

@router.get("/users/me/balance", response_model=schemas.UserBalance)
async def get_my_balance(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_invoice_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    balance_data = await lnbits.get_wallet_balance(x_api_key)
    
    if "error" in balance_data:
        raise HTTPException(status_code=500, detail="Failed to get balance")
    
    balance_msats = balance_data.get("balance", 0)
    
    return {
        "user_id": user.id,
        "balance_sats": balance_msats / 1000,
        "balance_msats": balance_msats
    }

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

