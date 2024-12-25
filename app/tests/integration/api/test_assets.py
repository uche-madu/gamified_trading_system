import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

pytestmark = pytest.mark.integration


def test_create_asset(asset_service):
    """Test creating a new asset."""
    # Arrange
    request_data = {"name": "Gold", "price": 1500.0}

    # Act
    response = client.post("/assets/", json=request_data)

    # Assert
    assert response.status_code == 201
    created_asset = asset_service.get_asset(asset_id=1)

    assert created_asset.name == "Gold"
    assert created_asset.price == 1500.0
    assert created_asset.id == 1
    assert response.json() == {"id": 1, "name": "Gold", "price": 1500.0}


def test_get_asset(asset_service):
    """
    Test retrieving an asset by ID.
    """
    # Arrange
    created_asset = asset_service.create_asset(name="Gold", price=1500.0)

    # Act
    response = client.get(f"/assets/{created_asset.id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": created_asset.id,
        "name": created_asset.name,
        "price": created_asset.price,
    }


def test_get_asset_not_found(postgres_db_session):
    """Test retrieving an asset that doesn't exist."""
    # Act
    response = client.get("/assets/999")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Asset with ID 999 not found."}


def test_update_asset(asset_service):
    """
    Test updating an existing asset.
    """
    # Arrange
    created_asset = asset_service.create_asset(name="Gold", price=1500.0)
    request_data = {"name": "Updated Gold", "price": 2000.0}

    # Act
    response = client.put(f"/assets/{created_asset.id}", json=request_data)

    # Assert
    updated_asset = asset_service.get_asset(created_asset.id)
    assert response.status_code == 200
    assert response.json() == {
        "id": updated_asset.id,
        "name": "Updated Gold",
        "price": 2000.0,
    }
    assert updated_asset.name == "Updated Gold"
    assert updated_asset.price == 2000.0


def test_update_asset_not_found(postgres_db_session):
    """Test updating an asset that doesn't exist."""
    # Act
    request_data = {"name": "Updated Gold", "price": 2000.0}
    response = client.put("/assets/999", json=request_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Asset with ID 999 not found."}


def test_delete_asset(asset_service):
    """
    Test deleting an asset by ID.
    """
    # Arrange
    created_asset = asset_service.create_asset(name="Gold", price=1500.0)

    # Act
    response = client.delete(f"/assets/{created_asset.id}")

    # Assert
    assert response.status_code == 204
    with pytest.raises(ValueError, match="Asset with ID .* not found."):
        asset_service.get_asset(created_asset.id)


def test_delete_asset_not_found(postgres_db_session):
    """
    Test deleting an asset that doesn't exist.
    """
    # Act
    response = client.delete("/assets/9999")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Asset with ID 9999 not found."}


def test_list_assets(asset_service):
    """
    Test listing all assets.
    """
    # Arrange
    asset_service.create_asset(name="Gold", price=1500.0)
    asset_service.create_asset(name="Silver", price=25.0)

    # Act
    response = client.get("/assets/")

    # Assert
    assets = asset_service.get_all_assets()
    assert response.status_code == 200
    assert response.json() == [
        {"id": assets[0].id, "name": "Gold", "price": 1500.0},
        {"id": assets[1].id, "name": "Silver", "price": 25.0},
    ]
