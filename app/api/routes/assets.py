from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_asset_service
from app.schemas.assets import AssetCreateRequest, AssetResponse, AssetUpdateRequest
from app.services.asset_service import AssetService

router = APIRouter()


@router.post("/", response_model=AssetResponse, status_code=201)
def create_asset(
    request: AssetCreateRequest,
    asset_service: AssetService = Depends(get_asset_service),
):
    """
    Create a new asset.
    """
    try:
        asset = asset_service.create_asset(name=request.name, price=request.price)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{asset_id}", response_model=AssetResponse, status_code=200)
def get_asset(asset_id: int, asset_service: AssetService = Depends(get_asset_service)):
    """
    Retrieve an asset by ID.
    """
    try:
        asset = asset_service.get_asset(asset_id)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{asset_id}", response_model=AssetResponse, status_code=200)
def update_asset(
    asset_id: int,
    request: AssetUpdateRequest,
    asset_service: AssetService = Depends(get_asset_service),
):
    """
    Update an asset's name or price.
    """
    try:
        asset = asset_service.update_asset(
            asset_id, name=request.name, price=request.price
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{asset_id}", status_code=204)
def delete_asset(
    asset_id: int, asset_service: AssetService = Depends(get_asset_service)
):
    """
    Delete an asset by ID.
    """
    try:
        asset_service.delete_asset(asset_id)
        return {"detail": "Asset successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[AssetResponse], status_code=200)
def list_assets(asset_service: AssetService = Depends(get_asset_service)):
    """
    List all available assets.
    """
    assets = asset_service.get_all_assets()
    return assets
