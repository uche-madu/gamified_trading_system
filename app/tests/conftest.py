import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tests.test_database import TestSessionLocal, test_engine

from app.core.database import Base, get_db
from app.main import app
from app.models import User

# SQLite test database URL for unit tests
SQLITE_TEST_DATABASE_URL = "sqlite:///:memory:"


# SQLite-specific setup
@pytest.fixture(scope="session")
def sqlite_engine():
    """
    Fixture to create an in-memory SQLite database engine for unit tests.
    """
    engine = create_engine(SQLITE_TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)  # Create schema
    yield engine
    Base.metadata.drop_all(bind=engine)  # Drop schema after tests


@pytest.fixture(scope="function")
def sqlite_db_session(sqlite_engine):
    """
    Fixture to provide a clean SQLite session for each test.
    """
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()

    # Clean tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="session")
def postgres_engine():
    """
    Fixture to create a PostgreSQL database engine for tests.
    """
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def postgres_db_session(postgres_engine):
    """
    Fixture to provide a PostgreSQL session with transaction rollback and override the get_db dependency.
    """
    session = TestSessionLocal(bind=postgres_engine)

    # Override the `get_db` dependency
    def _test_db_override():
        try:
            yield session
        finally:
            session.rollback()  # Rollback only after each test ends

    app.dependency_overrides[get_db] = _test_db_override

    # Clean tables and reset sequences before the test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
        session.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1;"))
    session.commit()

    try:
        yield session
    finally:
        # Cleanup after the test
        session.rollback()
        app.dependency_overrides.clear()
        session.close()


# User and data fixtures
@pytest.fixture
def sqlite_users(sqlite_db_session):
    """
    Create sample users for tests using SQLite.
    """
    sqlite_db_session.query(User).delete()

    # Create sample users
    user_data = [
        User(id=1, username="Alice", gem_count=150, rank=None, balance=500.0),
        User(id=2, username="Bob", gem_count=100, rank=None, balance=1000.0),
        User(id=3, username="Charlie", gem_count=200, rank=None, balance=300.0),
        User(id=4, username="Diana", gem_count=100, rank=None, balance=200.0),
        User(id=5, username="Eve", gem_count=4, trade_count=4, balance=2000.0),
        User(id=6, username="Frank", gem_count=14, trade_count=9, balance=1500.0),
    ]
    sqlite_db_session.bulk_save_objects(user_data)
    sqlite_db_session.commit()
    return user_data


@pytest.fixture
def postgres_users(postgres_db_session):
    """
    Create sample users for tests using PostgreSQL.
    """
    postgres_db_session.query(User).delete()

    # Create sample users
    user_data = [
        User(id=1, username="Alice", gem_count=150, rank=None, balance=500.0),
        User(id=2, username="Bob", gem_count=100, rank=None, balance=1000.0),
        User(id=3, username="Charlie", gem_count=200, rank=None, balance=300.0),
        User(id=4, username="Diana", gem_count=100, rank=None, balance=200.0),
        User(id=5, username="Eve", gem_count=4, trade_count=4, balance=2000.0),
        User(id=6, username="Frank", gem_count=14, trade_count=9, balance=1500.0),
    ]
    postgres_db_session.bulk_save_objects(user_data)
    postgres_db_session.commit()
    return user_data
