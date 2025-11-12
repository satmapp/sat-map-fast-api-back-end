from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommerceBase(BaseModel):
    name: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    website: Optional[str] = None
    category: str
    payment_method: str
    latitude: float
    longitude: float
    photo_url: Optional[str] = None

class CommerceCreate(CommerceBase):
    pass

class Commerce(CommerceBase):
    id: int
    verified: bool
    verification_count: int
    premium: bool
    submitted_by_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    wallet_id: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    sats_earned: int
    level: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VerificationCreate(BaseModel):
    commerce_id: int
    user_id: int

class Verification(BaseModel):
    id: int
    user_id: int
    commerce_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RewardResponse(BaseModel):
    user_id: int
    amount_sats: int
    reward_type: str

