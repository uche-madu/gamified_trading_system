import pytest
from app.models.user import User
from app.schemas.users import UserCreate  # Import UserCreate schema


def test_create_user(user_service, db_session):
    """Test creating a new user."""
    # Arrange
    user_data = UserCreate(user_id=1, username="Alice")

    # Act
    user = user_service.create_user(user_data=user_data)

    # Assert
    assert user.id == 1
    assert user.username == "Alice"
    assert user.gem_count == 0

    # Verify user exists in the database
    assert db_session.query(User).count() == 1
    db_user = db_session.query(User).filter_by(id=1).first()
    assert db_user.username == "Alice"


def test_get_user(user_service, db_session):
    """Test retrieving a user by ID."""
    # Arrange
    user_data = UserCreate(user_id=1, username="Alice")
    user_service.create_user(user_data=user_data)

    # Act
    user = user_service.get_user(user_id=1)

    # Assert
    assert user is not None
    assert user.id == 1
    assert user.username == "Alice"


def test_list_users(user_service, db_session):
    """Test listing all users."""
    # Arrange
    user_data_1 = UserCreate(user_id=1, username="Alice")
    user_data_2 = UserCreate(user_id=2, username="Bob")
    user_service.create_user(user_data=user_data_1)
    user_service.create_user(user_data=user_data_2)

    # Act
    users = user_service.list_users()

    # Assert
    assert len(users) == 2
    assert users[0].username == "Alice"
    assert users[1].username == "Bob"


def test_create_duplicate_user(user_service, db_session):
    """Test attempting to create a duplicate user."""
    # Arrange
    user_data = UserCreate(user_id=1, username="Alice")
    user_service.create_user(user_data=user_data)

    # Act & Assert: Expect a ValueError on duplicate user creation
    with pytest.raises(ValueError, match="User ID already exists."):
        user_service.create_user(user_data=user_data)
