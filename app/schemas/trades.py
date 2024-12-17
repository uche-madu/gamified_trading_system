from pydantic import BaseModel, ConfigDict


# Request schema for buying an asset
class BuyAssetRequest(BaseModel):
    asset_id: int
    name: str
    quantity: int
    price: float


# Request schema for selling an asset
class SellAssetRequest(BaseModel):
    asset_id: int
    name: str
    quantity: int
    price: float


# Response schema for trade actions
class TradeResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)
