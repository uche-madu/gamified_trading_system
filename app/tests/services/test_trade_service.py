from unittest.mock import MagicMock

import pytest

from app.models.user import User
from app.services.trade_service import TradeService


@pytest.fixture
def mock_user_service():
    """Mock the UserService."""
    return MagicMock()


@pytest.fixture
def mock_portfolio_service():
    """Mock the PortfolioService."""
    return MagicMock()


@pytest.fixture
def trade_service(db_session, mock_user_service, mock_portfolio_service):
    """Create the TradeService with real db_session but mocked dependencies."""
    return TradeService(
        db=db_session,
        portfolio_service=mock_portfolio_service,
        user_service=mock_user_service,
    )


def test_buy_asset(
    trade_service, db_session, mock_user_service, mock_portfolio_service
):
    """Test buying an asset increments trade count and gem count."""
    # Arrange
    user = User(id=1, username="Alice", trade_count=0, gem_count=0)
    db_session.add(user)
    db_session.commit()

    # Mock user retrieval
    mock_user_service.get_user.return_value = user

    # Mock portfolio addition
    mock_portfolio_service.add_asset_to_portfolio.return_value = MagicMock()

    # Act
    trade_service.buy_asset(user_id=1, asset_id=101, quantity=10, price=50.0)

    # Assert
    db_session.refresh(user)
    assert user.trade_count == 1
    assert user.gem_count == 1
    mock_user_service.get_user.assert_called_once_with(1)
    mock_portfolio_service.add_asset_to_portfolio.assert_called_once_with(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )


def test_sell_asset(
    trade_service, db_session, mock_user_service, mock_portfolio_service
):
    """Test selling an asset increments trade count and gem count."""
    # Arrange
    user = User(id=1, username="Bob", trade_count=2, gem_count=2)
    db_session.add(user)
    db_session.commit()

    # Mock user retrieval
    mock_user_service.get_user.return_value = user

    # Mock portfolio removal
    mock_portfolio_service.remove_asset.return_value = None

    # Act
    trade_service.sell_asset(user_id=1, asset_id=101, quantity=5)

    # Assert
    db_session.refresh(user)
    assert user.trade_count == 3
    assert user.gem_count == 3
    mock_user_service.get_user.assert_called_once_with(1)
    mock_portfolio_service.remove_asset.assert_called_once_with(
        user_id=1, asset_id=101, quantity=5
    )


def test_buy_asset_with_milestone_bonus(
    trade_service, db_session, mock_user_service, mock_portfolio_service
):
    """Test milestone bonus on the 5th trade."""
    # Arrange
    user = User(id=1, username="Charlie", trade_count=4, gem_count=4)
    db_session.add(user)
    db_session.commit()

    # Mock user retrieval
    mock_user_service.get_user.return_value = user

    # Mock portfolio addition
    mock_portfolio_service.add_asset_to_portfolio.return_value = MagicMock()

    # Act
    trade_service.buy_asset(user_id=1, asset_id=101, quantity=10, price=50.0)

    # Assert
    db_session.refresh(user)
    assert user.trade_count == 5
    assert user.gem_count == 10  # 4 gems + 1 (trade) + 5 (bonus)


def test_buy_asset_with_tenth_trade_bonus(
    trade_service, db_session, mock_user_service, mock_portfolio_service
):
    """Test milestone bonus on the 10th trade."""
    # Arrange
    user = User(id=1, username="Diana", trade_count=9, gem_count=9)
    db_session.add(user)
    db_session.commit()

    # Mock user retrieval
    mock_user_service.get_user.return_value = user

    # Mock portfolio addition
    mock_portfolio_service.add_asset_to_portfolio.return_value = MagicMock()

    # Act
    trade_service.buy_asset(user_id=1, asset_id=102, quantity=5, price=100.0)

    # Assert
    db_session.refresh(user)
    assert user.trade_count == 10
    assert user.gem_count == 20  # 9 gems + 1 (trade) + 10 (bonus)
