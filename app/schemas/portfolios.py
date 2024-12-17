from pydantic import BaseModel, ConfigDict
from typing import List

# Request schema for adding assets to a portfolio
class AddAssetRequest(BaseModel):
    asset_id: int  # ID of the asset from the global assets table
    quantity: int
    price: float  # Price at the time of adding the asset to the portfolio


# Request schema for creating a portfolio
class PortfolioRequest(BaseModel):
    user_id: int  # ID of the user for whom the portfolio is being created
    
# Response schema for a single asset in the portfolio
class PortfolioAssetResponse(BaseModel):
    asset_id: int  # Reference to the global Asset table
    name: str      # Name of the asset
    quantity: int  # Quantity held in the portfolio
    price: float   # Price at the time of adding the asset

    model_config = ConfigDict(from_attributes=True)


# Response schema for a user's portfolio
class PortfolioResponse(BaseModel):
    id: int  # Portfolio ID
    user_id: int
    assets: List[PortfolioAssetResponse]  # List of assets in the portfolio with their quantities and prices

    model_config = ConfigDict(from_attributes=True)


# Response schema for portfolio value
class PortfolioValueResponse(BaseModel):
    user_id: int
    portfolio_value: float
