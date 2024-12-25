from pydantic import BaseModel, Field


class BuyAssetRequest(BaseModel):
    asset_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero.")
    price: float = Field(..., gt=0, description="Price must be greater than zero.")
    name: str  # Optional, only used for logging or responses


class SellAssetRequest(BaseModel):
    asset_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero.")
    price: float = Field(..., gt=0, description="Price must be greater than zero.")
    name: str  # Optional, only used for logging or responses


class TradeResponse(BaseModel):
    message: str
