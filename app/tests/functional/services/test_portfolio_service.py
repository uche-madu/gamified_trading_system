import logging

import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.functional


def test_create_portfolio(portfolio_service, user_service):
    """Test creating a new portfolio."""
    # Arrange
    user = user_service.get_user(user_id=1)

    # Act
    portfolio = portfolio_service.create_portfolio(user_id=user.id)

    # Assert
    created_portfolio = portfolio_service.get_portfolio(user_id=user.id)
    assert created_portfolio.id == portfolio.id
    assert created_portfolio.user_id == user.id


def test_create_existing_portfolio(portfolio_service, user_service):
    """Test attempting to create a portfolio that already exists."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio_service.create_portfolio(user_id=user.id)

    # Act & Assert
    with pytest.raises(ValueError, match="Portfolio already exists."):
        portfolio_service.create_portfolio(user_id=1)


def test_add_asset_to_portfolio(portfolio_service, user_service, asset_service):
    """Test adding an asset to a portfolio."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio = portfolio_service.create_portfolio(user_id=user.id)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    # Act
    added_portfolio_asset = portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=10
    )

    # Assert
    assert added_portfolio_asset.portfolio_id == portfolio.id
    assert added_portfolio_asset.asset_id == asset.id
    assert added_portfolio_asset.quantity == 10
    assert added_portfolio_asset.avg_cost == asset.price
    assert added_portfolio_asset.name == asset.name


def test_add_existing_asset_to_portfolio(
    portfolio_service, user_service, asset_service
):
    """Test updating the quantity of an existing asset in a portfolio."""
    # Arrange
    user = user_service.get_user(user_id=2)
    portfolio = portfolio_service.create_portfolio(user_id=user.id)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=5
    )

    # Act
    # Update price of the asset
    asset_service.update_asset(asset_id=asset.id, price=40.0)
    updated_asset = asset_service.get_asset(asset_id=asset.id)

    # Add more units of the same asset at the new price
    updated_portfolio_asset = portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=updated_asset.id, quantity=15
    )

    # Assert
    assert updated_portfolio_asset.quantity == 20
    assert updated_portfolio_asset.avg_cost == 42.5
    assert updated_portfolio_asset.asset_id == asset.id
    assert updated_portfolio_asset.portfolio_id == portfolio.id
    assert updated_asset.id == asset.id
    assert updated_portfolio_asset.name == updated_asset.name


def test_remove_asset_partial(portfolio_service, user_service, asset_service):
    """Test removing part of an asset's quantity."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio = portfolio_service.create_portfolio(user_id=user.id)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=10
    )

    # Act
    portfolio_service.remove_asset_from_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=5
    )

    # Assert
    updated_portfolio_asset = portfolio_service.get_portfolio_asset(
        user_id=user.id, asset_id=asset.id
    )
    assert updated_portfolio_asset.quantity == 5
    assert updated_portfolio_asset.avg_cost == 50.0
    assert updated_portfolio_asset.asset_id == asset.id
    assert updated_portfolio_asset.portfolio_id == portfolio.id


def test_remove_asset_entire(portfolio_service, user_service, asset_service):
    """Test removing an entire asset from a portfolio."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio_service.create_portfolio(user_id=user.id)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=10
    )

    # Act
    portfolio_service.remove_asset_from_portfolio(
        user_id=user.id, asset_id=user.id, quantity=10
    )

    # Assert
    with pytest.raises(ValueError, match="Asset with ID 1 not found in portfolio."):
        portfolio_service.get_portfolio_asset(user_id=user.id, asset_id=asset.id)


def test_remove_asset_insufficient_quantity(
    portfolio_service, user_service, asset_service
):
    """Test attempting to remove more quantity than exists."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio_service.create_portfolio(user_id=user.id)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=5
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Insufficient quantity to sell."):
        portfolio_service.remove_asset_from_portfolio(
            user_id=user.id, asset_id=asset.id, quantity=10
        )


def test_list_portfolio_assets(portfolio_service, user_service, asset_service):
    """Test listing all assets in a portfolio."""
    # Arrange
    user = user_service.get_user(user_id=2)
    portfolio_service.create_portfolio(user_id=user.id)
    asset1 = asset_service.create_asset(name="Stock A", price=50.0)
    asset2 = asset_service.create_asset(name="Stock B", price=100.0)

    # Add assets to the portfolio
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset1.id, quantity=5
    )
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset2.id, quantity=5
    )

    # Act
    assets = portfolio_service.list_portfolio_assets(user_id=user.id)

    # Assert
    assert len(assets) == 2
    assert assets[0].asset_id == 1
    assert assets[1].asset_id == 2
    assert assets[0].quantity == 5
    assert assets[1].quantity == 5
    assert assets[0].avg_cost == 50.0
    assert assets[1].avg_cost == 100.0


def test_calculate_portfolio_value(portfolio_service, user_service, asset_service):
    """Test calculating the total portfolio value."""
    # Arrange
    user = user_service.get_user(user_id=2)
    portfolio_service.create_portfolio(user_id=user.id)
    asset1 = asset_service.create_asset(name="Stock A", price=50.0)
    asset2 = asset_service.create_asset(name="Stock B", price=100.0)

    # Add assets to the portfolio
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset1.id, quantity=5
    )
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset2.id, quantity=5
    )

    # Act
    total_value = portfolio_service.calculate_portfolio_value(user_id=user.id)

    # Assert
    assert total_value == 750.0  # (5 * 50) + (5 * 100)


def test_calculate_portfolio_value_empty(portfolio_service):
    """Test calculating value for an empty portfolio."""
    # Arrange
    portfolio_service.create_portfolio(user_id=1)

    # Act
    total_value = portfolio_service.calculate_portfolio_value(user_id=1)

    # Assert
    assert total_value == 0.0


def test_get_portfolio_asset(portfolio_service, user_service, asset_service):
    """Test retrieving a specific asset from a portfolio."""
    # Arrange
    user = user_service.get_user(user_id=1)
    portfolio = portfolio_service.create_portfolio(user_id=1)
    asset = asset_service.create_asset(name="Stock A", price=50.0)

    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=10
    )

    # Act
    portfolio_asset = portfolio_service.get_portfolio_asset(
        user_id=user.id, asset_id=asset.id
    )

    # Assert
    assert portfolio_asset is not None
    assert portfolio_asset.portfolio_id == portfolio.id
    assert portfolio_asset.asset_id == 1
    assert portfolio_asset.quantity == 10
    assert portfolio_asset.avg_cost == 50.0
    assert portfolio_asset.name == "Stock A"


def test_get_portfolio_asset_not_found(portfolio_service):
    """Test retrieving a non-existing asset from a portfolio."""
    # Arrange
    portfolio_service.create_portfolio(user_id=1)

    # Act & Assert
    with pytest.raises(ValueError, match="Asset with ID 101 not found in portfolio."):
        portfolio_service.get_portfolio_asset(user_id=1, asset_id=101)


def test_buy_asset_with_fifth_trade_bonus(
    portfolio_service, user_service, asset_service
):
    """Test milestone bonus on the 5th trade."""
    # Arrange
    user = user_service.get_user(user_id=5)
    asset = asset_service.create_asset(name="Ruby", price=50.0)
    portfolio_service.create_portfolio(user_id=user.id)

    # Act
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=10
    )

    # Assert
    portfolio_assets = portfolio_service.get_portfolio_asset(
        user_id=user.id, asset_id=asset.id
    )
    updated_user = user_service.get_user(user_id=user.id)
    assert updated_user.trade_count == 5
    assert updated_user.gem_count == 10  # 4 gems + 1 (trade) + 5 (bonus)
    assert updated_user.balance == 1500.0  # 2000.0 - (10 * 50)
    assert portfolio_assets.quantity == 10
    assert portfolio_assets.avg_cost == 50.0


def test_buy_asset_with_tenth_trade_bonus(
    portfolio_service, user_service, asset_service
):
    """Test milestone bonus on the 10th trade."""
    # Arrange
    user = user_service.get_user(user_id=6)
    asset = asset_service.create_asset(name="Diamond", price=100.0)
    portfolio_service.create_portfolio(user_id=user.id)

    # Act
    portfolio_service.add_asset_to_portfolio(
        user_id=user.id, asset_id=asset.id, quantity=5
    )

    # Assert
    portfolio_asset = portfolio_service.get_portfolio_asset(
        user_id=user.id, asset_id=asset.id
    )
    updated_user = user_service.get_user(user_id=user.id)
    assert updated_user.trade_count == 10
    assert updated_user.gem_count == 25  # 14 gems + 1 (trade) + 10 (bonus)
    assert updated_user.balance == 1000.0  # 1500.0 - (5 * 100)
    assert portfolio_asset.quantity == 5
    assert portfolio_asset.avg_cost == 100.0
