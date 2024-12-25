from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.dependencies import get_portfolio_service
from app.schemas.portfolios import (
    AddAssetRequest,
    PortfolioAssetRemoveResponse,
    PortfolioAssetResponse,
    PortfolioRequest,
    PortfolioResponse,
    PortfolioValueResponse,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.post("/", response_model=PortfolioResponse, status_code=201)
def create_portfolio(
    request: PortfolioRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Create a new portfolio for a user.
    """
    try:
        portfolio = portfolio_service.create_portfolio(user_id=request.user_id)
        return PortfolioResponse(id=portfolio.id, user_id=portfolio.user_id, assets=[])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{user_id}/assets/", response_model=PortfolioAssetResponse, status_code=201
)
def add_asset(
    user_id: int,
    request: AddAssetRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Add an asset to a user's portfolio.
    """
    try:
        portfolio_asset = portfolio_service.add_asset_to_portfolio(
            user_id=user_id, asset_id=request.asset_id, quantity=request.quantity
        )

        return PortfolioAssetResponse(
            asset_id=portfolio_asset.asset_id,
            name=portfolio_asset.asset.name,
            quantity=portfolio_asset.quantity,
            avg_cost=portfolio_asset.avg_cost,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{user_id}/assets/{asset_id}", response_model=PortfolioAssetRemoveResponse
)
def remove_asset(
    user_id: int,
    asset_id: int,
    quantity: Annotated[int, Query(gt=0, description="Quantity to remove")],
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Remove or sell an asset from a user's portfolio.
    - If the quantity is fully removed, the asset will be deleted.
    - If only a portion is sold, the asset will be updated.
    """
    try:
        portfolio_asset = portfolio_service.remove_asset_from_portfolio(
            user_id, asset_id, quantity
        )
        logger.info(f"Quantity: {portfolio_asset}")
        if portfolio_asset.quantity == 0:
            return PortfolioAssetRemoveResponse(
                detail="Asset fully removed from the portfolio.",
                asset_id=asset_id,
                remaining_quantity=None,
            )
        return PortfolioAssetRemoveResponse(
            detail="Asset quantity successfully updated.",
            asset_id=asset_id,
            remaining_quantity=portfolio_asset.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.get("/{user_id}/value", response_model=PortfolioValueResponse, status_code=200)
def calculate_portfolio_value(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Calculate the total value of a user's portfolio.
    """
    try:
        value = portfolio_service.calculate_portfolio_value(user_id)
        return PortfolioValueResponse(user_id=user_id, portfolio_value=value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/", response_model=PortfolioResponse, status_code=200)
def get_portfolio(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Retrieve a user's portfolio and its assets.
    """
    try:
        portfolio = portfolio_service.get_portfolio(user_id)
        portfolio_assets = portfolio_service.list_portfolio_assets(user_id)

        # Map PortfolioAsset and joined Asset data to PortfolioAssetResponse
        assets_response = [
            PortfolioAssetResponse(
                asset_id=pa.asset_id,
                name=pa.asset.name,
                quantity=pa.quantity,
                avg_cost=pa.avg_cost,
            )
            for pa in portfolio_assets
        ]

        return PortfolioResponse(
            id=portfolio.id, user_id=portfolio.user_id, assets=assets_response
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{user_id}/assets/{asset_id}",
    response_model=PortfolioAssetResponse,
    status_code=200,
)
def get_portfolio_asset(
    user_id: int,
    asset_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Retrieve a specific asset from a user's portfolio.
    """
    try:
        portfolio_asset = portfolio_service.get_portfolio_asset(user_id, asset_id)
        return PortfolioAssetResponse(
            asset_id=portfolio_asset.asset_id,
            name=portfolio_asset.asset.name,
            quantity=portfolio_asset.quantity,
            avg_cost=portfolio_asset.avg_cost,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{user_id}/assets/", response_model=list[PortfolioAssetResponse], status_code=200
)
def list_portfolio_assets(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    List all assets in a user's portfolio.
    """
    try:
        portfolio_assets = portfolio_service.list_portfolio_assets(user_id)
        return [
            PortfolioAssetResponse(
                asset_id=pa.asset_id,
                name=pa.asset.name,
                quantity=pa.quantity,
                avg_cost=pa.avg_cost,
            )
            for pa in portfolio_assets
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
