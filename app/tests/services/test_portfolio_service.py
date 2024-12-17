import pytest

from app.models.asset import Asset
from app.models.portfolio import Portfolio
from app.models.portfolio_assets import PortfolioAsset


def test_create_portfolio(portfolio_service, db_session):
    """Test creating a new portfolio."""
    # Act
    portfolio = portfolio_service.create_portfolio(user_id=1)

    # Assert
    assert portfolio.id is not None
    assert portfolio.user_id == 1

    db_portfolio = db_session.query(Portfolio).filter(Portfolio.user_id == 1).first()
    assert db_portfolio is not None
    assert db_portfolio.user_id == 1


def test_create_existing_portfolio(portfolio_service, db_session):
    """Test attempting to create a portfolio that already exists."""
    # Arrange
    existing_portfolio = Portfolio(user_id=1)
    db_session.add(existing_portfolio)
    db_session.commit()

    # Act & Assert
    with pytest.raises(ValueError, match="Portfolio already exists."):
        portfolio_service.create_portfolio(user_id=1)


def test_add_asset_to_portfolio(portfolio_service, db_session):
    """Test adding an asset to a portfolio."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset = Asset(id=101, name="Stock A", price=50.0)
    db_session.add(asset)
    db_session.commit()

    # Act
    portfolio_asset = portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )

    # Assert
    assert portfolio_asset.portfolio_id == portfolio.id
    assert portfolio_asset.asset_id == 101
    assert portfolio_asset.quantity == 10
    assert portfolio_asset.price == 50.0

    db_portfolio_asset = (
        db_session.query(PortfolioAsset).filter_by(asset_id=101).first()
    )
    assert db_portfolio_asset is not None
    assert db_portfolio_asset.quantity == 10


def test_add_existing_asset_to_portfolio(portfolio_service, db_session):
    """Test updating the quantity of an existing asset in a portfolio."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset = Asset(id=101, name="Stock A", price=50.0)
    db_session.add(asset)
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=5, price=50.0
    )

    # Act
    updated_portfolio_asset = portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )

    # Assert
    assert updated_portfolio_asset.quantity == 15
    db_portfolio_asset = (
        db_session.query(PortfolioAsset).filter_by(asset_id=101).first()
    )
    assert db_portfolio_asset.quantity == 15


def test_remove_asset_partial(portfolio_service, db_session):
    """Test removing part of an asset's quantity."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset = Asset(id=101, name="Stock A", price=50.0)
    db_session.add(asset)
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )

    # Act
    portfolio_service.remove_asset(user_id=1, asset_id=101, quantity=5)

    # Assert
    db_portfolio_asset = (
        db_session.query(PortfolioAsset).filter_by(asset_id=101).first()
    )
    assert db_portfolio_asset.quantity == 5


def test_remove_asset_entire(portfolio_service, db_session):
    """Test removing an entire asset from a portfolio."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset = Asset(id=101, name="Stock A", price=50.0)
    db_session.add(asset)
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )

    # Act
    portfolio_service.remove_asset(user_id=1, asset_id=101, quantity=10)

    # Assert
    db_portfolio_asset = (
        db_session.query(PortfolioAsset).filter_by(asset_id=101).first()
    )
    assert db_portfolio_asset is None


def test_remove_asset_insufficient_quantity(portfolio_service, db_session):
    """Test attempting to remove more quantity than exists."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset = Asset(id=101, name="Stock A", price=50.0)
    db_session.add(asset)
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=5, price=50.0
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Cannot remove 10 units of asset 101."):
        portfolio_service.remove_asset(user_id=1, asset_id=101, quantity=10)


def test_list_portfolio_assets(portfolio_service, db_session):
    """Test listing all assets in a portfolio."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset1 = Asset(id=101, name="Stock A", price=50.0)
    asset2 = Asset(id=102, name="Stock B", price=100.0)
    db_session.add_all([asset1, asset2])
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )
    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=102, quantity=5, price=100.0
    )

    # Act
    assets = portfolio_service.list_portfolio_assets(user_id=1)

    # Assert
    assert len(assets) == 2
    assert assets[0].asset_id == 101
    assert assets[1].asset_id == 102


def test_calculate_portfolio_value(portfolio_service, db_session):
    """Test calculating the total portfolio value."""
    # Arrange
    portfolio = Portfolio(user_id=1)
    db_session.add(portfolio)
    asset1 = Asset(id=101, name="Stock A", price=50.0)
    asset2 = Asset(id=102, name="Stock B", price=100.0)
    db_session.add_all([asset1, asset2])
    db_session.commit()

    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=101, quantity=10, price=50.0
    )
    portfolio_service.add_asset_to_portfolio(
        user_id=1, asset_id=102, quantity=5, price=100.0
    )

    # Act
    total_value = portfolio_service.calculate_portfolio_value(user_id=1)

    # Assert
    assert total_value == 1000.0  # (10 * 50) + (5 * 100)


def test_calculate_portfolio_value_empty(portfolio_service):
    """Test calculating value for an empty portfolio."""
    # Arrange
    portfolio_service.create_portfolio(user_id=1)

    # Act
    total_value = portfolio_service.calculate_portfolio_value(user_id=1)

    # Assert
    assert total_value == 0.0
