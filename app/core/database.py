import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Build the database URL dynamically from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for database sessions in FastAPI routes.
    Creates a new SQLAlchemy session for each request and closes it after use.
    """
    db = SessionLocal()
    print(f"Using main database session: {db.bind.url}")
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database schema using Alembic migrations instead of direct creation.
    Not directly anymore through `Base.metadata.create_all(bind=engine)`
    """

    # Inform developers to use Alembic migrations.
    raise NotImplementedError(
        "Database initialization is managed via Alembic migrations. "
        "Run `alembic upgrade head` to apply migrations."
    )
