from pydantic import BaseModel, ConfigDict


# Schema for creating an asset
class AssetCreateRequest(BaseModel):
    name: str
    price: float


# Schema for updating an asset
class AssetUpdateRequest(BaseModel):
    name: str | None = None
    price: float | None = None


# Schema for asset response
class AssetResponse(BaseModel):
    id: int
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)
