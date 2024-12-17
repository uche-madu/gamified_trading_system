import pytest

from app.models.asset import Asset


def test_create_asset(asset_service, db_session):
    """Test creating a new asset."""
    # Act
    asset = asset_service.create_asset(name="Gold", price=1500.0)

    # Assert
    assert asset.id is not None
    assert asset.name == "Gold"
    assert asset.price == 1500.0

    db_asset = db_session.query(Asset).filter(Asset.name == "Gold").first()
    assert db_asset is not None
    assert db_asset.name == "Gold"
    assert db_asset.price == 1500.0


def test_get_asset(asset_service, db_session):
    """Test retrieving an asset by ID."""
    # Arrange
    asset = Asset(name="Gold", price=1500.0)
    db_session.add(asset)
    db_session.commit()

    # Act
    retrieved_asset = asset_service.get_asset(asset_id=asset.id)

    # Assert
    assert retrieved_asset.id == asset.id
    assert retrieved_asset.name == "Gold"
    assert retrieved_asset.price == 1500.0


def test_get_asset_not_found(asset_service):
    """Test retrieving a non-existent asset."""
    # Act & Assert
    with pytest.raises(ValueError, match="Asset with ID 999 not found."):
        asset_service.get_asset(asset_id=999)


def test_update_asset(asset_service, db_session):
    """Test updating an asset's name and price."""
    # Arrange
    asset = Asset(name="Gold", price=1500.0)
    db_session.add(asset)
    db_session.commit()

    # Act
    updated_asset = asset_service.update_asset(
        asset_id=asset.id, name="Updated Gold", price=2000.0
    )

    # Assert
    assert updated_asset.name == "Updated Gold"
    assert updated_asset.price == 2000.0

    db_asset = db_session.query(Asset).filter(Asset.id == asset.id).first()
    assert db_asset.name == "Updated Gold"
    assert db_asset.price == 2000.0


def test_update_asset_partial(asset_service, db_session):
    """Test partially updating an asset (only price)."""
    # Arrange
    asset = Asset(name="Gold", price=1500.0)
    db_session.add(asset)
    db_session.commit()

    # Act
    updated_asset = asset_service.update_asset(asset_id=asset.id, price=1800.0)

    # Assert
    assert updated_asset.name == "Gold"  # Name remains the same
    assert updated_asset.price == 1800.0

    db_asset = db_session.query(Asset).filter(Asset.id == asset.id).first()
    assert db_asset.name == "Gold"
    assert db_asset.price == 1800.0


def test_update_asset_not_found(asset_service):
    """Test updating a non-existent asset."""
    # Act & Assert
    with pytest.raises(ValueError, match="Asset with ID 999 not found."):
        asset_service.update_asset(asset_id=999, name="Invalid Asset")


def test_delete_asset(asset_service, db_session):
    """Test deleting an asset."""
    # Arrange
    asset = Asset(name="Gold", price=1500.0)
    db_session.add(asset)
    db_session.commit()

    # Act
    asset_service.delete_asset(asset_id=asset.id)

    # Assert
    db_asset = db_session.query(Asset).filter(Asset.id == asset.id).first()
    assert db_asset is None


def test_delete_asset_not_found(asset_service):
    """Test deleting a non-existent asset."""
    # Act & Assert
    with pytest.raises(ValueError, match="Asset with ID 999 not found."):
        asset_service.delete_asset(asset_id=999)


def test_get_all_assets(asset_service, db_session):
    """Test retrieving all assets."""
    # Arrange
    asset1 = Asset(name="Gold", price=1500.0)
    asset2 = Asset(name="Silver", price=25.0)
    db_session.add_all([asset1, asset2])
    db_session.commit()

    # Act
    assets = asset_service.get_all_assets()

    # Assert
    assert len(assets) == 2
    assert assets[0].name == "Gold"
    assert assets[1].name == "Silver"
