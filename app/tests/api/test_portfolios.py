from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_portfolio_service
from app.main import app
from app.models.asset import Asset
from app.models.portfolio_assets import PortfolioAsset

# Initialize TestClient
client = TestClient(app)


@pytest.fixture
def mock_portfolio_service():
    """Fixture to mock the PortfolioService."""
    return MagicMock()


@pytest.fixture(autouse=True)
def override_dependency(mock_portfolio_service):
    """
    Override the PortfolioService dependency for all tests in this module.
    """
    app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_service
    yield
    app.dependency_overrides.clear()


def test_create_portfolio(mock_portfolio_service):
    """
    Test creating a new portfolio for a user.
    """
    # Arrange
    request_data = {"user_id": 1}
    mock_response = {"id": 1, "user_id": 1, "assets": []}

    # Mock service response
    mock_portfolio_service.create_portfolio.return_value = MagicMock(id=1, user_id=1)

    # Act
    response = client.post("/portfolios/", json=request_data)

    # Assertions
    assert response.status_code == 201
    assert response.json() == mock_response
    mock_portfolio_service.create_portfolio.assert_called_once_with(user_id=1)


def test_add_asset(mock_portfolio_service):
    """
    Test adding an asset to a user's portfolio.
    """
    user_id = 1
    request_data = {
        "asset_id": 101,
        "quantity": 10,
        "price": 1500.0,
    }

    # Mock response
    mock_portfolio_service.add_asset_to_portfolio.return_value = PortfolioAsset(
        asset_id=101, quantity=10, price=1500.0, asset=Asset(id=101, name="Gold")
    )

    # Send request
    response = client.post(f"/portfolios/{user_id}/assets/", json=request_data)

    # Assertions
    assert response.status_code == 201
    assert response.json() == {
        "asset_id": 101,
        "name": "Gold",
        "quantity": 10,
        "price": 1500.0,
    }

    # Match call with keyword arguments
    mock_portfolio_service.add_asset_to_portfolio.assert_called_once_with(
        user_id=user_id, asset_id=101, quantity=10, price=1500.0
    )


def test_remove_asset(mock_portfolio_service):
    """
    Test removing an asset from the portfolio.
    """
    user_id = 1
    asset_id = 101
    quantity = 5

    # Mock successful removal
    mock_portfolio_service.remove_asset.return_value = None

    # Send request
    response = client.delete(
        f"/portfolios/{user_id}/assets/{asset_id}?quantity={quantity}"
    )

    # Assertions
    assert response.status_code == 204
    mock_portfolio_service.remove_asset.assert_called_once_with(
        user_id, asset_id, quantity
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


def test_get_portfolio(mock_portfolio_service):
    """
    Test retrieving a user's portfolio and its assets.
    """
    user_id = 1

    # Mock portfolio and assets
    mock_portfolio_service.get_portfolio.return_value = MagicMock(id=1, user_id=user_id)
    mock_portfolio_service.list_portfolio_assets.return_value = [
        PortfolioAsset(
            asset_id=101, quantity=10, price=1500.0, asset=Asset(id=101, name="Gold")
        ),
        PortfolioAsset(
            asset_id=102, quantity=5, price=500.0, asset=Asset(id=102, name="Silver")
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
            {"asset_id": 101, "name": "Gold", "quantity": 10, "price": 1500.0},
            {"asset_id": 102, "name": "Silver", "quantity": 5, "price": 500.0},
        ],
    }
    mock_portfolio_service.get_portfolio.assert_called_once_with(user_id)
    mock_portfolio_service.list_portfolio_assets.assert_called_once_with(user_id)
