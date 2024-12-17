from sqlalchemy.orm import Session
from app.models.asset import Asset
from sqlalchemy.exc import SQLAlchemyError


class AssetService:
    def __init__(self, db: Session):
        self.db = db

    def create_asset(self, name: str, price: float) -> Asset:
        """
        Create a new asset.
        """
        try:
            asset = Asset(name=name, price=price)
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
            return asset
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error creating asset.") from e

    def get_asset(self, asset_id: int) -> Asset:
        """
        Retrieve an asset by ID.
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found.")
        return asset

    def update_asset(self, asset_id: int, name: str | None = None, price: float | None = None) -> Asset:
        """
        Update an asset's name and/or price.
        """
        try:
            asset = self.get_asset(asset_id)
            if name:
                asset.name = name
            if price:
                asset.price = price

            self.db.commit()
            self.db.refresh(asset)
            return asset
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error updating asset.") from e

    def delete_asset(self, asset_id: int) -> None:
        """
        Delete an asset by ID.
        """
        try:
            asset = self.get_asset(asset_id)
            self.db.delete(asset)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error deleting asset.") from e

    def get_all_assets(self) -> list[Asset]:
        """
        Retrieve all assets.
        """
        return self.db.query(Asset).all()
