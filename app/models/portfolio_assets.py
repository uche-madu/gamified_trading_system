from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.core.database import Base


class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_cost = Column(Float, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")
    asset = relationship("Asset")

    @hybrid_property
    def name(self):
        return self.asset.name
