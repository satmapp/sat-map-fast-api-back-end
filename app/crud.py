from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from app import models, schemas

def create_user(db: Session, wallet_id: str):
    db_user = models.User(wallet_id=wallet_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_wallet(db: Session, wallet_id: str):
    return db.query(models.User).filter(models.User.wallet_id == wallet_id).first()

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
    
    user = get_user(db, user_id)
    user.sats_earned += amount_sats
    
    db.commit()
    db.refresh(db_reward)
    return db_reward

def get_user_balance(db: Session, user_id: int):
    user = get_user(db, user_id)
    return user.sats_earned if user else 0

