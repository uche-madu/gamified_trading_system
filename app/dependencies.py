from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.services.portfolio_service import PortfolioService
from app.services.trade_service import TradeService
from app.services.ranking_service import RankingService
from app.services.asset_service import AssetService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency to provide UserService with the required database session.
    """
    return UserService(db=db)


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    """
    Dependency to provide PortfolioService with the required database session.
    """
    return PortfolioService(db=db)


def get_trade_service(
    db: Session = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    user_service: UserService = Depends(get_user_service)
) -> TradeService:
    """
    Dependency to provide TradeService with the required database session and related services.
    """
    return TradeService(db=db, portfolio_service=portfolio_service, user_service=user_service)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    """
    Dependency to provide RankingService with the required database session.
    """
    return RankingService(db=db)


def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    """
    Dependency to provide AssetService with the required database session.
    """
    return AssetService(db)
