import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables for testing
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


# Create a test-specific SQLAlchemy engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create a configured "Session" class for tests
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Dependency override for tests
def get_test_db():
    db = TestSessionLocal()
    logger.info(f"Using test database session: {db.bind.url}")
    try:
        yield db
    finally:
        db.close()
