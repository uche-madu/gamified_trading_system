from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    gem_count = Column(Integer, default=0, nullable=False)
    rank = Column(Integer, default=0, nullable=False)
    trade_count = Column(Integer, default=0, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)

    portfolio = relationship("Portfolio", back_populates="user")
