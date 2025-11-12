from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app import schemas, crud, models
from app.database import get_db

router = APIRouter()

@router.post("/commerces", response_model=schemas.Commerce)
def create_commerce(commerce: schemas.CommerceCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_commerce(db, commerce, user_id)

@router.get("/commerces", response_model=List[schemas.Commerce])
def get_commerces(verified: Optional[bool] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_commerces(db, verified, skip, limit)

@router.get("/commerces/pending", response_model=List[schemas.Commerce])
def get_pending_commerces(db: Session = Depends(get_db)):
    return crud.get_pending_commerces(db)

@router.get("/commerces/{commerce_id}", response_model=schemas.Commerce)
def get_commerce(commerce_id: int, db: Session = Depends(get_db)):
    commerce = crud.get_commerce(db, commerce_id)
    if not commerce:
        raise HTTPException(status_code=404, detail="Commerce not found")
    return commerce

@router.post("/commerces/{commerce_id}/verify")
async def verify_commerce(commerce_id: int, user_id: int, db: Session = Depends(get_db)):
    commerce = crud.get_commerce(db, commerce_id)
    if not commerce:
        raise HTTPException(status_code=404, detail="Commerce not found")
    
    result = crud.create_verification(db, user_id, commerce_id)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Already verified by this user")
    
    if result["verified"]:
        submitter_reward = crud.create_reward(db, commerce.submitted_by_id, commerce_id, 150, "submission")
        
        verifiers = db.query(models.Verification).filter(
            models.Verification.commerce_id == commerce_id
        ).all()
        
        for verification in verifiers:
            crud.create_reward(db, verification.user_id, commerce_id, 50, "verification")
        
        return {
            "message": "Commerce verified successfully",
            "verified": True,
            "rewards_distributed": True
        }
    
    return {
        "message": "Verification recorded",
        "verified": False,
        "count": commerce.verification_count
    }

