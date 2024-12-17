import pytest
from services.asset_service import AssetService
from services.ranking_service import RankingService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base  # Ensure the same Base is used
from app.models import User  # Import models to register them with Base
from app.services.portfolio_service import PortfolioService
from app.services.trade_service import TradeService
from app.services.user_service import UserService

# Use SQLite for testing (in-memory database)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """
    Fixture to create an in-memory SQLite database engine for testing.
    This is separate from the application's PostgreSQL engine.
    """
    engine = create_engine(TEST_DATABASE_URL)

    # Create all tables before running tests
    Base.metadata.create_all(bind=engine)  # Use the same Base as the application
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Fixture to create a new database session for each test function.
    Ensures a clean state between tests by clearing tables.
    """
    # Create a new session for the test
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clean up the database state before the test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    try:
        yield session
    finally:
        # Rollback and close session after the test
        session.rollback()
        session.close()


@pytest.fixture
def user_service(db_session):
    """
    Fixture to initialize UserService with the test database session.
    """
    return UserService(db_session)


@pytest.fixture
def portfolio_service(db_session):
    """
    Fixture to initialize PortfolioService with the test database session.
    """
    return PortfolioService(db_session)


@pytest.fixture
def trade_service(db_session, portfolio_service, user_service):
    """
    Fixture to initialize TradeService with the test database session and services.
    """
    return TradeService(db_session, portfolio_service, user_service)


@pytest.fixture
def ranking_service(db_session):
    """Fixture to create an instance of RankingService with a database session."""
    return RankingService(db_session)


@pytest.fixture
def asset_service(db_session):
    """Fixture to create an instance of AssetService with a database session."""
    return AssetService(db_session)


@pytest.fixture
def users(db_session):
    """
    Fixture to create and return sample User instances.
    """
    # Ensure no existing data (clean slate)
    db_session.query(User).delete()

    # Create sample users
    user_data = [
        User(id=1, username="Alice", gem_count=15, rank=None),
        User(id=2, username="Bob", gem_count=10, rank=None),
        User(id=3, username="Charlie", gem_count=20, rank=None),
        User(id=4, username="Diana", gem_count=10, rank=None),
    ]
    db_session.bulk_save_objects(user_data)  # Bulk insert for efficiency
    db_session.commit()
    return user_data
