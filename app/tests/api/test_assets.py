import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.schemas.assets import AssetResponse, AssetCreateRequest, AssetUpdateRequest
from app.dependencies import get_asset_service

client = TestClient(app)

@pytest.fixture
def mock_asset_service():
    """Fixture for Mock AssetService."""
    return MagicMock()

@pytest.fixture(autouse=True)
def override_asset_service(mock_asset_service):
    """
    Override the TradeService dependency with the mock.
    """
    app.dependency_overrides[get_asset_service] = lambda: mock_asset_service
    yield
    app.dependency_overrides.clear()


def test_create_asset(mock_asset_service):
    """Test creating a new asset."""
    # Arrange
    request_data = {"name": "Gold", "price": 1500.0}
    mock_response = AssetResponse(id=1, name="Gold", price=1500.0)
    mock_asset_service.create_asset.return_value = mock_response

    # Act
    response = client.post("/assets/", json=request_data)

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Gold",
        "price": 1500.0
    }
    mock_asset_service.create_asset.assert_called_once_with(name="Gold", price=1500.0)


def test_get_asset(mock_asset_service):
    """Test retrieving an asset by ID."""
    # Arrange
    asset_id = 1
    mock_response = AssetResponse(id=1, name="Gold", price=1500.0)
    mock_asset_service.get_asset.return_value = mock_response

    # Act
    response = client.get(f"/assets/{asset_id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Gold",
        "price": 1500.0
    }
    mock_asset_service.get_asset.assert_called_once_with(asset_id)


def test_get_asset_not_found(mock_asset_service):
    """Test retrieving an asset that doesn't exist."""
    # Arrange
    asset_id = 999
    mock_asset_service.get_asset.side_effect = ValueError("Asset with ID 999 not found.")

    # Act
    response = client.get(f"/assets/{asset_id}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Asset with ID 999 not found."}
    mock_asset_service.get_asset.assert_called_once_with(asset_id)


def test_update_asset(mock_asset_service):
    """Test updating an existing asset."""
    # Arrange
    asset_id = 1
    request_data = {"name": "Updated Gold", "price": 2000.0}
    mock_response = AssetResponse(id=1, name="Updated Gold", price=2000.0)
    mock_asset_service.update_asset.return_value = mock_response

    # Act
    response = client.put(f"/assets/{asset_id}", json=request_data)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Updated Gold",
        "price": 2000.0
    }
    mock_asset_service.update_asset.assert_called_once_with(1, name="Updated Gold", price=2000.0)


def test_update_asset_not_found(mock_asset_service):
    """Test updating an asset that doesn't exist."""
    # Arrange
    asset_id = 999
    request_data = {"name": "Updated Gold", "price": 2000.0}
    mock_asset_service.update_asset.side_effect = ValueError("Asset with ID 999 not found.")

    # Act
    response = client.put(f"/assets/{asset_id}", json=request_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Asset with ID 999 not found."}
    mock_asset_service.update_asset.assert_called_once_with(999, name="Updated Gold", price=2000.0)

def test_delete_asset(mock_asset_service):
    """Test deleting an asset by ID."""
    # Arrange
    asset_id = 1

    # Act
    response = client.delete(f"/assets/{asset_id}")

    # Assert
    assert response.status_code == 204
    mock_asset_service.delete_asset.assert_called_once_with(asset_id)


def test_delete_asset_not_found(mock_asset_service):
    """Test deleting an asset that doesn't exist."""
    # Arrange
    asset_id = 999
    mock_asset_service.delete_asset.side_effect = ValueError("Asset with ID 999 not found.")

    # Act
    response = client.delete(f"/assets/{asset_id}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Asset with ID 999 not found."}
    mock_asset_service.delete_asset.assert_called_once_with(asset_id)


def test_list_assets(mock_asset_service):
    """Test listing all assets."""
    # Arrange
    mock_response = [
        AssetResponse(id=1, name="Gold", price=1500.0),
        AssetResponse(id=2, name="Silver", price=25.0),
    ]
    mock_asset_service.get_all_assets.return_value = mock_response

    # Act
    response = client.get("/assets/")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Gold", "price": 1500.0},
        {"id": 2, "name": "Silver", "price": 25.0},
    ]
    mock_asset_service.get_all_assets.assert_called_once()
