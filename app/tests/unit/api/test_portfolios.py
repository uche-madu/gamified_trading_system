from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from loguru import logger
from schemas.portfolios import (
    AddAssetRequest,
    PortfolioRequest,
)
from services.portfolio_service import PortfolioService

from app.dependencies import get_portfolio_service
from app.main import app
from app.models import Asset, PortfolioAsset

pytestmark = pytest.mark.unit

# Initialize TestClient
client = TestClient(app)


@pytest.fixture
def mock_portfolio_service():
    """Fixture to mock the PortfolioService."""
    return MagicMock(spec=PortfolioService)


@pytest.fixture(autouse=True)
def override_dependency(mock_portfolio_service):
    """
    Override the PortfolioService dependency for all tests in this module.
    """
    app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_service
    yield
    app.dependency_overrides.clear()


# Test create_portfolio route
def test_create_portfolio(mock_portfolio_service):
    # Arrange
    request_data = PortfolioRequest(user_id=1)
    mock_portfolio_service.create_portfolio.return_value = MagicMock(id=1, user_id=1)

    # Act
    response = client.post("/portfolios/", json=request_data.model_dump())

    # Assert
    assert response.status_code == 201
    assert response.json() == {"id": 1, "user_id": 1, "assets": []}
    mock_portfolio_service.create_portfolio.assert_called_once_with(user_id=1)


# Test add_asset route
def test_add_asset(mock_portfolio_service):
    # Arrange
    user_id = 1
    request_data = AddAssetRequest(asset_id=101, quantity=10, price=1500.0)

    # Mock PortfolioAsset with joined Asset details
    mock_asset = MagicMock(spec=Asset)
    mock_asset.id = 101
    mock_asset.name = "Gold"
    mock_asset.price = 1500.0

    mock_portfolio_asset = MagicMock(spec=PortfolioAsset)
    mock_portfolio_asset.asset_id = mock_asset.id
    mock_portfolio_asset.quantity = 10
    mock_portfolio_asset.avg_cost = 1500.0
    mock_portfolio_asset.asset = mock_asset

    mock_portfolio_service.add_asset_to_portfolio.return_value = mock_portfolio_asset

    # Act
    response = client.post(
        f"/portfolios/{user_id}/assets/", json=request_data.model_dump()
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "asset_id": 101,
        "name": "Gold",
        "quantity": 10,
        "avg_cost": 1500.0,
    }
    mock_portfolio_service.add_asset_to_portfolio.assert_called_once_with(
        user_id=user_id, asset_id=request_data.asset_id, quantity=request_data.quantity
    )


def test_remove_asset_partial_quantity(mock_portfolio_service):
    """
    Test removing part of the quantity of an asset from the portfolio.
    """
    user_id = 5
    asset_id = 101
    quantity_to_remove = 5

    # Mock the service's return value
    mock_portfolio_asset = MagicMock()
    mock_portfolio_asset.quantity = 5  # Remaining quantity after removal
    mock_portfolio_service.remove_asset_from_portfolio.return_value = (
        mock_portfolio_asset
    )

    # Act: Send the DELETE request
    response = client.delete(
        f"/portfolios/{user_id}/assets/{asset_id}?quantity={quantity_to_remove}"
    )

    logger.info(f"The Response: {response.json()}")
    # Assert: Verify the response
    assert response.status_code == 200

    assert response.json() == {
        "detail": "Asset quantity successfully updated.",
        "asset_id": asset_id,
        "remaining_quantity": 5,
    }

    # Assert: Verify the service method was called correctly
    mock_portfolio_service.remove_asset_from_portfolio.assert_called_once_with(
        user_id, asset_id, quantity_to_remove
    )


def test_remove_asset_full_quantity(mock_portfolio_service):
    """
    Test removing all of the quantity of an asset from the portfolio.
    """
    user_id = 5
    asset_id = 101
    quantity_to_remove = 10

    # Mock the service's return value
    mock_portfolio_asset = MagicMock()
    mock_portfolio_asset.quantity = 0  # Asset fully removed
    mock_portfolio_service.remove_asset_from_portfolio.return_value = (
        mock_portfolio_asset
    )

    # Act: Send the DELETE request
    response = client.delete(
        f"/portfolios/{user_id}/assets/{asset_id}?quantity={quantity_to_remove}"
    )

    # Assert: Verify the response
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Asset fully removed from the portfolio.",
        "asset_id": asset_id,
        "remaining_quantity": None,
    }

    # Verify the service method was called correctly
    mock_portfolio_service.remove_asset_from_portfolio.assert_called_once_with(
        user_id, asset_id, quantity_to_remove
    )


def test_calculate_portfolio_value(mock_portfolio_service):
    """
    Test calculating the total portfolio value.
    """
    user_id = 1

    # Mock response
    mock_portfolio_service.calculate_portfolio_value.return_value = 25000.0

    # Send request
    response = client.get(f"/portfolios/{user_id}/value")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"user_id": user_id, "portfolio_value": 25000.0}
    mock_portfolio_service.calculate_portfolio_value.assert_called_once_with(user_id)


def test_list_portfolio_assets(mock_portfolio_service):
    """
    Test retrieving a user's portfolio and its assets.
    """
    user_id = 1

    # Mock portfolio and assets
    mock_portfolio = MagicMock(id=1, user_id=user_id)
    mock_portfolio_service.get_portfolio.return_value = mock_portfolio
    mock_portfolio_service.list_portfolio_assets.return_value = [
        PortfolioAsset(
            asset_id=101, quantity=10, avg_cost=1500.0, asset=Asset(id=101, name="Gold")
        ),
        PortfolioAsset(
            asset_id=102, quantity=5, avg_cost=500.0, asset=Asset(id=102, name="Silver")
        ),
    ]

    # Send request
    response = client.get(f"/portfolios/{user_id}/")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user_id": user_id,
        "assets": [
            {"asset_id": 101, "name": "Gold", "quantity": 10, "avg_cost": 1500.0},
            {"asset_id": 102, "name": "Silver", "quantity": 5, "avg_cost": 500.0},
        ],
    }
    mock_portfolio_service.get_portfolio.assert_called_once_with(user_id)
    mock_portfolio_service.list_portfolio_assets.assert_called_once_with(user_id)


def test_get_portfolio_asset(mock_portfolio_service):
    """
    Test retrieving a specific asset from a user's portfolio.
    """
    user_id = 1
    asset_id = 101

    # Mock portfolio asset
    mock_portfolio_service.get_portfolio_asset.return_value = PortfolioAsset(
        asset_id=asset_id,
        quantity=10,
        avg_cost=1500.0,
        asset=Asset(id=asset_id, name="Gold"),
    )

    # Send request
    response = client.get(f"/portfolios/{user_id}/assets/{asset_id}")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "asset_id": asset_id,
        "name": "Gold",
        "quantity": 10,
        "avg_cost": 1500.0,
    }
    mock_portfolio_service.get_portfolio_asset.assert_called_once_with(
        user_id, asset_id
    )
