import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build the database URL dynamically from environment variables
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

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
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    Models are imported dynamically to avoid circular import issues.
    """
    if os.getenv("ENV") == "TESTING":
        return  # Skip table creation in tests
    
    # Import all models to ensure they are registered with Base
    from app.models import User, Portfolio, Asset, PortfolioAsset
    Base.metadata.create_all(bind=engine)
