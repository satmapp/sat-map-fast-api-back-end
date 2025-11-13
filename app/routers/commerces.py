from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from app import schemas, crud, models
from app.database import get_db
from app.services import lnbits

router = APIRouter()

@router.post("/commerces", response_model=schemas.Commerce)
async def create_commerce(
    commerce: schemas.CommerceCreate,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_invoice_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return crud.create_commerce(db, commerce, user.id)


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
async def verify_commerce(
    commerce_id: int,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_invoice_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    commerce = crud.get_commerce(db, commerce_id)
    if not commerce:
        raise HTTPException(status_code=404, detail="Commerce not found")
    
    result = crud.create_verification(db, user.id, commerce_id)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Already verified by this user")
    
    if result["verified"]:
        submitter = crud.get_user(db, commerce.submitted_by_id)
        
        print(f"[VERIFY] Sending 150 sats to submitter {submitter.username}")
        submitter_result = await lnbits.send_sats_to_wallet(
            submitter.lnbits_invoice_key,
            150,
            f"SatMap reward: commerce submission verified"
        )
        
        if "error" not in submitter_result:
            crud.create_reward(db, commerce.submitted_by_id, commerce_id, 150, "submission")
            print(f"[VERIFY] Submitter reward recorded")
        else:
            print(f"[VERIFY] ERROR sending to submitter: {submitter_result}")
        
        verifiers = db.query(models.Verification).filter(
            models.Verification.commerce_id == commerce_id
        ).all()
        
        rewards_sent = 0
        for verification in verifiers:
            verifier = crud.get_user(db, verification.user_id)
            print(f"[VERIFY] Sending 50 sats to verifier {verifier.username}")
            verifier_result = await lnbits.send_sats_to_wallet(
                verifier.lnbits_invoice_key,
                50,
                f"SatMap reward: commerce verification"
            )
            
            if "error" not in verifier_result:
                crud.create_reward(db, verification.user_id, commerce_id, 50, "verification")
                rewards_sent += 1
                print(f"[VERIFY] Verifier reward recorded")
            else:
                print(f"[VERIFY] ERROR sending to verifier: {verifier_result}")
        
        return {
            "message": "Commerce verified successfully",
            "verified": True,
            "rewards_distributed": True,
            "rewards_sent": rewards_sent + 1
        }
    
    return {
        "message": "Verification recorded",
        "verified": False,
        "count": commerce.verification_count
    }

