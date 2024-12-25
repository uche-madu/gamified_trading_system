import pytest

from app.schemas.users import UserCreate

pytestmark = pytest.mark.functional


def test_create_user(user_service):
    """Test creating a new user with zero balance."""
    # Arrange
    user_data = UserCreate(username="Amaka")

    # Act
    user = user_service.create_user(user_data=user_data)

    # Assert
    assert user.id is not None
    assert user.username == "Amaka"
    assert user.gem_count == 0
    assert user.balance == 0.0
    assert user.trade_count == 0


def test_get_user(user_service):
    """Test retrieving a user by ID."""
    # Act
    fetched_user = user_service.get_user(user_id=1)

    # Assert
    assert fetched_user is not None
    assert fetched_user.username == "Alice"
    assert fetched_user.balance == 500.0
    assert fetched_user.gem_count == 150
    assert fetched_user.trade_count == 0


def test_list_users(user_service):
    """Test listing all users."""
    # Act
    users = user_service.list_users()

    # Assert
    assert len(users) == 6
    assert users[0].username == "Alice"
    assert users[1].username == "Bob"
    assert users[5].trade_count == 9


def test_create_duplicate_user(user_service):
    """Test attempting to create a user with a duplicate username."""
    # Arrange
    user_data = UserCreate(username="Alice")

    # Act & Assert: Expect a ValueError on duplicate username
    with pytest.raises(ValueError, match="Username already exists."):
        user_service.create_user(user_data=user_data)


def test_deposit_balance(user_service):
    """Test depositing into a user's balance."""
    # Arrange
    user = user_service.get_user(user_id=1)

    # Act
    user_service.deposit_balance(user_id=user.id, amount=200.0)

    # Assert
    updated_user = user_service.get_user(user_id=1)
    assert updated_user.balance == 700.0


def test_withdraw_balance(user_service):
    """Test withdrawing from a user's balance."""
    # Arrange
    user = user_service.get_user(user_id=1)

    # Act
    user_service.withdraw_balance(user_id=user.id, amount=300.0)

    # Assert
    updated_user = user_service.get_user(user_id=1)
    assert updated_user.balance == 200.0


def test_withdraw_insufficient_balance(user_service):
    """Test withdrawing an amount greater than the user's balance."""
    # Arrange
    user = user_service.get_user(user_id=1)

    # Act & Assert: Expect a ValueError for insufficient funds
    with pytest.raises(ValueError, match="Insufficient funds."):
        user_service.withdraw_balance(user_id=user.id, amount=600.0)
