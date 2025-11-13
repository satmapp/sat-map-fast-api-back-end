from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from app import models, schemas

def create_user_with_wallet(
    db: Session, 
    username: str, 
    lnbits_user_id: Optional[str],
    lnbits_wallet_id: str, 
    lnbits_admin_key: str, 
    lnbits_invoice_key: str
):
    db_user = models.User(
        username=username,
        lnbits_user_id=lnbits_user_id,
        lnbits_wallet_id=lnbits_wallet_id,
        lnbits_admin_key=lnbits_admin_key,
        lnbits_invoice_key=lnbits_invoice_key
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_invoice_key(db: Session, invoice_key: str):
    return db.query(models.User).filter(models.User.lnbits_invoice_key == invoice_key).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_commerce(db: Session, commerce: schemas.CommerceCreate, user_id: int):
    db_commerce = models.Commerce(**commerce.dict(), submitted_by_id=user_id)
    db.add(db_commerce)
    db.commit()
    db.refresh(db_commerce)
    return db_commerce

def get_commerces(db: Session, verified: Optional[bool] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Commerce)
    if verified is not None:
        query = query.filter(models.Commerce.verified == verified)
    return query.offset(skip).limit(limit).all()

def get_commerce(db: Session, commerce_id: int):
    return db.query(models.Commerce).filter(models.Commerce.id == commerce_id).first()

def get_pending_commerces(db: Session):
    return db.query(models.Commerce).filter(models.Commerce.verified == False).all()

def create_verification(db: Session, user_id: int, commerce_id: int):
    existing = db.query(models.Verification).filter(
        and_(
            models.Verification.user_id == user_id,
            models.Verification.commerce_id == commerce_id
        )
    ).first()
    
    if existing:
        return None
    
    db_verification = models.Verification(user_id=user_id, commerce_id=commerce_id)
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    
    commerce = get_commerce(db, commerce_id)
    commerce.verification_count += 1
    
    if commerce.verification_count >= 3 and not commerce.verified:
        commerce.verified = True
        db.commit()
        return {"verified": True, "verification": db_verification}
    
    db.commit()
    return {"verified": False, "verification": db_verification}

def create_reward(db: Session, user_id: int, commerce_id: int, amount_sats: int, reward_type: str):
    db_reward = models.Reward(
        user_id=user_id,
        commerce_id=commerce_id,
        amount_sats=amount_sats,
        reward_type=reward_type
    )
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

