import pytest

from app.models import User
from app.services import AssetService, PortfolioService, RankingService, UserService


@pytest.fixture
def portfolio_service(postgres_db_session):
    """
    Fixture to initialize PortfolioService with the PostgreSQL test database session.
    """
    return PortfolioService(postgres_db_session)


@pytest.fixture
def user_service(postgres_db_session):
    """
    Fixture to initialize UserService with the PostgreSQL test database session.
    """
    return UserService(postgres_db_session)


@pytest.fixture
def ranking_service(postgres_db_session):
    """
    Fixture to initialize RankingService with the PostgreSQL test database session.
    """
    return RankingService(postgres_db_session)


@pytest.fixture
def asset_service(postgres_db_session):
    """
    Fixture to initialize AssetService with the PostgreSQL test database session.
    """
    return AssetService(postgres_db_session)


@pytest.fixture
def postgres_users(postgres_db_session):
    """
    Create sample users for tests using PostgreSQL.
    """
    postgres_db_session.query(User).delete()

    # Create sample users
    user_data = [
        User(id=1, username="Alice", gem_count=150, rank=0, balance=500.0),
        User(id=2, username="Bob", gem_count=100, rank=0, balance=1000.0),
        User(id=3, username="Charlie", gem_count=200, rank=0, balance=300.0),
        User(id=4, username="Diana", gem_count=100, rank=0, balance=200.0),
        User(id=5, username="Eve", gem_count=4, trade_count=4, balance=2000.0),
        User(id=6, username="Frank", gem_count=14, trade_count=9, balance=1500.0),
    ]
    postgres_db_session.bulk_save_objects(user_data)
    postgres_db_session.commit()
    return user_data
