from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_portfolio_service
from app.schemas.portfolios import (
    AddAssetRequest,
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
    Add or update an asset in a user's portfolio.
    """
    try:
        portfolio_asset = portfolio_service.add_asset_to_portfolio(
            user_id=user_id,
            asset_id=request.asset_id,
            quantity=request.quantity,
            price=request.price,
        )

        return PortfolioAssetResponse(
            asset_id=portfolio_asset.asset_id,
            name=portfolio_asset.asset.name,  # Joined asset name
            quantity=portfolio_asset.quantity,
            price=portfolio_asset.price,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}/assets/{asset_id}", status_code=204)
def remove_asset(
    user_id: int,
    asset_id: int,
    quantity: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """
    Remove or decrease the quantity of an asset in a user's portfolio.
    """
    try:
        portfolio_service.remove_asset(user_id, asset_id, quantity)
        return {"detail": "Asset successfully removed or updated."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        return {"user_id": user_id, "portfolio_value": value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/", response_model=PortfolioResponse)
def get_portfolio(
    user_id: int, portfolio_service: PortfolioService = Depends(get_portfolio_service)
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
                name=pa.asset.name,  # Joined asset name
                quantity=pa.quantity,
                price=pa.price,
            )
            for pa in portfolio_assets
        ]

        return PortfolioResponse(
            id=portfolio.id,
            user_id=portfolio.user_id,
            assets=assets_response,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
