import pytest

from app.models import User
from app.services import AssetService, PortfolioService, RankingService, UserService


@pytest.fixture
def portfolio_service(sqlite_db_session):
    """
    Fixture to initialize PortfolioService with the SQLite test database session.
    """
    return PortfolioService(sqlite_db_session)


@pytest.fixture
def user_service(sqlite_db_session):
    """
    Fixture to initialize UserService with the SQLite test database session.
    """
    return UserService(sqlite_db_session)


@pytest.fixture
def ranking_service(sqlite_db_session):
    """
    Fixture to initialize RankingService with the SQLite test database session.
    """
    return RankingService(sqlite_db_session)


@pytest.fixture
def asset_service(sqlite_db_session):
    """
    Fixture to initialize AssetService with the SQLite test database session.
    """
    return AssetService(sqlite_db_session)


# User and data fixtures
@pytest.fixture(autouse=True)
def sqlite_users(sqlite_db_session):
    """
    Create sample users for tests using SQLite.
    """
    sqlite_db_session.query(User).delete()

    # Create sample users
    user_data = [
        User(id=1, username="Alice", gem_count=150, rank=0, balance=500.0),
        User(id=2, username="Bob", gem_count=100, rank=0, balance=1000.0),
        User(id=3, username="Charlie", gem_count=200, rank=0, balance=300.0),
        User(id=4, username="Diana", gem_count=100, rank=0, balance=200.0),
        User(id=5, username="Eve", gem_count=4, trade_count=4, balance=2000.0),
        User(id=6, username="Frank", gem_count=14, trade_count=9, balance=1500.0),
    ]
    sqlite_db_session.bulk_save_objects(user_data)
    sqlite_db_session.commit()
    return user_data
