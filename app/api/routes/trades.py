from fastapi import APIRouter, HTTPException, Depends
from app.schemas.trades import BuyAssetRequest, SellAssetRequest, TradeResponse
from app.services.trade_service import TradeService
from app.dependencies import get_trade_service

router = APIRouter()

@router.post("/{user_id}/buy/", response_model=TradeResponse, status_code=201)
def buy_asset(
    user_id: int,
    request: BuyAssetRequest,
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Buy an asset for a user.
    """
    try:
        # Perform the buy operation
        trade_service.buy_asset(user_id, request.asset_id, request.quantity, request.price)

        # Calculate total value
        total_value = request.quantity * request.price

        # Return formatted response
        return TradeResponse(
            message=(
                f"Successfully purchased {request.quantity} units of '{request.name}' at "
                f"{request.price} per unit, for a total value of {total_value}."
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/sell/", response_model=TradeResponse, status_code=201)
def sell_asset(
    user_id: int,
    request: SellAssetRequest,
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Sell an asset for a user.
    """
    try:
        # Perform the sell operation
        trade_service.sell_asset(user_id, request.asset_id, request.quantity)

        # Calculate total value
        total_value = request.quantity * request.price  # Assume price passed in the request

        # Return formatted response
        return TradeResponse(
            message=(
                f"Successfully sold {request.quantity} units of '{request.name}' at "
                f"{request.price} per unit, for a total value of {total_value}."
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
