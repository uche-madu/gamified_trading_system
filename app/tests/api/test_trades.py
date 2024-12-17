from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_trade_service
from app.main import app

# Test client
client = TestClient(app)


# Correct Mock TradeService
@pytest.fixture
def mock_trade_service():
    """Fixture for Mock TradeService."""
    return MagicMock()


@pytest.fixture(autouse=True)
def override_trade_service(mock_trade_service):
    """
    Override the TradeService dependency with the mock.
    """
    app.dependency_overrides[get_trade_service] = lambda: mock_trade_service
    yield
    app.dependency_overrides.clear()


def test_buy_asset(mock_trade_service):
    """
    Test buying an asset for a user.
    """
    # Arrange
    user_id = 1
    request_data = {
        "asset_id": 101,
        "name": "Gold",
        "quantity": 10,
        "price": 1500.0,
    }

    # Mock service response
    mock_trade_service.buy_asset.return_value = None

    # Act
    response = client.post(f"/trades/{user_id}/buy/", json=request_data)

    # Assertions
    assert response.status_code == 201
    assert response.json() == {
        "message": "Successfully purchased 10 units of 'Gold' at 1500.0 per unit, for a total value of 15000.0."
    }
    mock_trade_service.buy_asset.assert_called_once_with(user_id, 101, 10, 1500.0)


def test_sell_asset(mock_trade_service):
    """
    Test selling an asset for a user.
    """
    # Arrange
    user_id = 1
    request_data = {"asset_id": 101, "name": "Gold", "quantity": 5, "price": 1500.0}

    # Mock service response
    mock_trade_service.sell_asset.return_value = None

    # Act
    response = client.post(f"/trades/{user_id}/sell/", json=request_data)

    # Assertions
    assert response.status_code == 201
    assert response.json() == {
        "message": "Successfully sold 5 units of 'Gold' at 1500.0 per unit, for a total value of 7500.0."
    }
    mock_trade_service.sell_asset.assert_called_once_with(user_id, 101, 5)


def test_buy_asset_invalid_data(mock_trade_service):
    """
    Test buying an asset with invalid data (missing fields).
    """
    user_id = 1
    request_data = {"asset_id": 101, "quantity": 10, "price": 1500.0}  # Missing 'name'

    # Act
    response = client.post(f"/trades/{user_id}/buy/", json=request_data)

    # Assertions
    assert response.status_code == 422  # Unprocessable Entity
    assert "name" in response.json()["detail"][0]["loc"]


def test_sell_asset_invalid_data(mock_trade_service):
    """
    Test selling an asset with invalid data (missing fields).
    """
    user_id = 1
    request_data = {"asset_id": 101}  # Missing 'name' and 'quantity'

    # Act
    response = client.post(f"/trades/{user_id}/sell/", json=request_data)

    # Assertions
    assert response.status_code == 422  # Unprocessable Entity
    assert "name" in response.json()["detail"][0]["loc"]
    assert "quantity" in response.json()["detail"][1]["loc"]
