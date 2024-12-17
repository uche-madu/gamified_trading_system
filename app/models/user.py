# models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    gem_count = Column(Integer, default=0, nullable=False)
    rank = Column(Integer, nullable=True)
    trade_count = Column(Integer, default=0, nullable=False)

    portfolio = relationship("Portfolio", back_populates="user")
