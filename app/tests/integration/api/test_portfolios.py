import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

pytestmark = pytest.mark.integration


def test_create_portfolio(user_service, portfolio_service, postgres_users):
    """
    Test creating a new portfolio for a user.
    """
    # Arrange
    user = user_service.get_user(user_id=1)

    # Act
    response = client.post("/portfolios/", json={"user_id": user.id})

    # Assert
    assert response.status_code == 201
    portfolio = portfolio_service.get_portfolio(user.id)
    assert portfolio.user_id == user.id
    assert response.json() == {"id": portfolio.id, "user_id": user.id, "assets": []}


def test_add_asset(user_service, asset_service, portfolio_service, postgres_users):
    """
    Test adding an asset to a user's portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    asset = asset_service.create_asset(name="Gold", price=100.0)
    portfolio_service.create_portfolio(user.id)

    request_data = {"asset_id": asset.id, "quantity": 10, "price": asset.price}

    # Act
    response = client.post(f"/portfolios/{user.id}/assets/", json=request_data)

    # Assert
    portfolio_asset = portfolio_service.get_portfolio_asset(user.id, asset.id)
    assert response.status_code == 201
    assert portfolio_asset.quantity == 10
    assert portfolio_asset.avg_cost == asset.price
    assert response.json() == {
        "asset_id": asset.id,
        "name": "Gold",
        "quantity": 10,
        "avg_cost": 100.0,
    }


def test_remove_asset(user_service, asset_service, portfolio_service, postgres_users):
    """
    Test removing an asset from the portfolio.
    """
    # Arrange
    # Get user and create the asset using the service
    user = user_service.get_user(user_id=5)
    created_asset = asset_service.create_asset(name="Gold", price=100.0)

    # Create a portfolio and add the asset to the portfolio
    portfolio_service.create_portfolio(user.id)
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=created_asset.id, quantity=10
    )

    # Retrieve the portfolio asset to check the initial state
    portfolio_asset = portfolio_service.get_portfolio_asset(user.id, created_asset.id)

    # Assert: Verify initial state
    assert portfolio_asset.quantity == 10

    # Act: Remove part of the asset's quantity
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=5"
    )

    # Assert: Verify the response and updated portfolio state
    assert response.status_code == 200

    # Reload the portfolio asset to check the updated state
    updated_portfolio_asset = portfolio_service.get_portfolio_asset(
        user.id, created_asset.id
    )
    assert updated_portfolio_asset.quantity == 5


def test_remove_asset_partial_quantity(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test removing part of the quantity of an asset from the portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    created_asset = asset_service.create_asset(name="Gold", price=100.0)

    portfolio_service.create_portfolio(user.id)
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=created_asset.id, quantity=10
    )

    # Act: Remove part of the asset's quantity
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=5"
    )

    # Assert: Verify the response and updated portfolio state
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Asset quantity successfully updated.",
        "asset_id": created_asset.id,
        "remaining_quantity": 5,
    }

    # Verify the portfolio state
    updated_portfolio_asset = portfolio_service.get_portfolio_asset(
        user.id, created_asset.id
    )
    assert updated_portfolio_asset.quantity == 5


def test_remove_asset_full_quantity(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test removing the full quantity of an asset from the portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    created_asset = asset_service.create_asset(name="Silver", price=50.0)

    portfolio_service.create_portfolio(user.id)
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=created_asset.id, quantity=10
    )

    # Act: Remove the entire asset quantity
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=10"
    )

    # Assert: Verify the response and updated portfolio state
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Asset fully removed from the portfolio.",
        "asset_id": created_asset.id,
        "remaining_quantity": None,
    }

    # Verify the asset is removed from the portfolio
    with pytest.raises(ValueError):
        portfolio_service.get_portfolio_asset(user.id, created_asset.id)


def test_remove_asset_insufficient_quantity(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test removing more quantity than available in the portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    created_asset = asset_service.create_asset(name="Platinum", price=200.0)

    portfolio_service.create_portfolio(user.id)
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=created_asset.id, quantity=5
    )

    # Act: Attempt to remove more than the available quantity
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=10"
    )

    # Assert: Verify the response
    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient quantity to sell."}


def test_remove_asset_nonexistent_asset(
    user_service, portfolio_service, postgres_users
):
    """
    Test removing a nonexistent asset from the portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    portfolio_service.create_portfolio(user.id)

    # Act: Attempt to remove an asset that doesn't exist in the portfolio
    response = client.delete(f"/portfolios/{user.id}/assets/999?quantity=5")

    # Assert: Verify the response
    assert response.status_code == 400
    assert response.json() == {"detail": "Asset with ID 999 not found in portfolio."}


def test_remove_asset_invalid_quantity(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test removing an asset with an invalid quantity (e.g., negative or zero).
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    created_asset = asset_service.create_asset(name="Copper", price=20.0)

    portfolio_service.create_portfolio(user.id)
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=created_asset.id, quantity=10
    )

    # Act: Attempt to remove an invalid quantity (zero)
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=0"
    )

    # Assert: Verify the response
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be greater than 0"

    # Act: Attempt to remove an invalid quantity (negative)
    response = client.delete(
        f"/portfolios/{user.id}/assets/{created_asset.id}?quantity=-5"
    )

    # Assert: Verify the response
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be greater than 0"


def test_calculate_portfolio_value(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test calculating the total portfolio value.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    portfolio_service.create_portfolio(user.id)
    asset1 = asset_service.create_asset(name="Gold", price=100.0)
    asset2 = asset_service.create_asset(name="Silver", price=25.0)

    portfolio_service.add_asset_to_portfolio(user.id, asset1.id, quantity=10)
    portfolio_service.add_asset_to_portfolio(user.id, asset2.id, quantity=20)

    # Act
    response = client.get(f"/portfolios/{user.id}/value")

    # Assert
    total_value = portfolio_service.calculate_portfolio_value(user.id)
    assert response.status_code == 200
    assert response.json() == {"user_id": user.id, "portfolio_value": total_value}


def test_get_portfolio(user_service, asset_service, portfolio_service, postgres_users):
    """
    Test retrieving a user's portfolio and its assets.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    portfolio_service.create_portfolio(user.id)
    asset1 = asset_service.create_asset(name="Gold", price=100.0)
    asset2 = asset_service.create_asset(name="Silver", price=25.0)

    portfolio_service.add_asset_to_portfolio(user.id, asset1.id, quantity=10)
    portfolio_service.add_asset_to_portfolio(user.id, asset2.id, quantity=5)

    # Act
    response = client.get(f"/portfolios/{user.id}/")

    # Assert
    portfolio = portfolio_service.get_portfolio(user.id)
    assert response.status_code == 200
    assert response.json() == {
        "id": portfolio.id,
        "user_id": user.id,
        "assets": [
            {"asset_id": asset1.id, "name": "Gold", "quantity": 10, "avg_cost": 100.0},
            {"asset_id": asset2.id, "name": "Silver", "quantity": 5, "avg_cost": 25.0},
        ],
    }


# Create tests for list_portfolio_assets and get_portfolio_asset
def test_list_portfolio_assets(
    user_service, asset_service, portfolio_service, postgres_users
):
    """
    Test listing all assets in a user's portfolio.
    """
    # Arrange
    user = user_service.get_user(user_id=5)
    portfolio_service.create_portfolio(user.id)
    asset1 = asset_service.create_asset(name="Gold", price=100.0)
    asset2 = asset_service.create_asset(name="Silver", price=25.0)
    asset3 = asset_service.create_asset(name="Platinum", price=200.0)

    portfolio_service.add_asset_to_portfolio(user.id, asset1.id, quantity=10)
    portfolio_service.add_asset_to_portfolio(user.id, asset2.id, quantity=5)
    portfolio_service.add_asset_to_portfolio(user.id, asset3.id, quantity=2)

    # Act
    response = client.get(f"/portfolios/{user.id}/assets/")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {"asset_id": asset1.id, "name": "Gold", "quantity": 10, "avg_cost": 100.0},
        {"asset_id": asset2.id, "name": "Silver", "quantity": 5, "avg_cost": 25.0},
        {"asset_id": asset3.id, "name": "Platinum", "quantity": 2, "avg_cost": 200.0},
    ]
    assert len(response.json()) == 3
