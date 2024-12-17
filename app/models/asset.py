from sqlalchemy import Column, Float, Integer, String

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)
