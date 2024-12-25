from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field


# Request schema for adding assets to a portfolio
class AddAssetRequest(BaseModel):
    asset_id: int = Field(
        ..., gt=0, description="ID must be greater than zero."
    )  # ID of the asset from the global assets table
    quantity: int = Field(..., gt=0, description="ID must be greater than zero.")


# Request schema for creating a portfolio
class PortfolioRequest(BaseModel):
    user_id: int = Field(
        ..., gt=0, description="ID must be greater than zero."
    )  # ID of the user for whom the portfolio is being created


# Response schema for a single asset in the portfolio
class PortfolioAssetResponse(BaseModel):
    asset_id: int  # Reference to the global Asset table
    name: str  # Name of the asset
    quantity: int  # Quantity held in the portfolio
    avg_cost: float  # Average cost of acquiring the asset

    model_config = ConfigDict(from_attributes=True)


class PortfolioAssetRemoveResponse(BaseModel):
    detail: str  # Message indicating the result of the operation
    asset_id: Union[int, None] = None  # ID of the asset affected (optional)
    remaining_quantity: Union[int, None] = (
        None  # Remaining quantity of the asset (optional)
    )


# Response schema for a user's portfolio
class PortfolioResponse(BaseModel):
    id: int  # Portfolio ID
    user_id: int
    assets: List[
        PortfolioAssetResponse
    ]  # List of assets in the portfolio with their quantities and prices

    model_config = ConfigDict(from_attributes=True)


# Response schema for portfolio value
class PortfolioValueResponse(BaseModel):
    user_id: int
    portfolio_value: float
