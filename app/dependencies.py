from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import AssetService, PortfolioService, RankingService, UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency to provide UserService with the required database session.
    """
    logger.info(f"get_user_service called with db session: {db.bind.url}")
    return UserService(db=db)


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    """
    Dependency to provide PortfolioService with the required database session.
    """
    logger.info(f"get_portfolio_service called with db session: {db.bind.url}")
    return PortfolioService(db=db)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    """
    Dependency to provide RankingService with the required database session.
    """
    logger.info(f"get_ranking_service called with db session: {db.bind.url}")
    return RankingService(db=db)


def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    """
    Dependency to provide AssetService with the required database session.
    """
    logger.info(f"get_asset_service called with db session: {db.bind.url}")
    return AssetService(db)
