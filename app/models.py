from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(String, unique=True, index=True)
    sats_earned = Column(Integer, default=0)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    commerces = relationship("Commerce", back_populates="submitter")
    verifications = relationship("Verification", back_populates="user")
    rewards = relationship("Reward", back_populates="user")

class Commerce(Base):
    __tablename__ = "commerces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    category = Column(String)
    payment_method = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    photo_url = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    verification_count = Column(Integer, default=0)
    premium = Column(Boolean, default=False)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    submitter = relationship("User", back_populates="commerces")
    verifications = relationship("Verification", back_populates="commerce")
    rewards = relationship("Reward", back_populates="commerce")

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    commerce_id = Column(Integer, ForeignKey("commerces.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="verifications")
    commerce = relationship("Commerce", back_populates="verifications")

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    commerce_id = Column(Integer, ForeignKey("commerces.id"))
    amount_sats = Column(Integer)
    reward_type = Column(String)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="rewards")
    commerce = relationship("Commerce", back_populates="rewards")

