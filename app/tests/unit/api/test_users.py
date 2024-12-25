from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_user_service
from app.main import app
from app.models.user import User
from app.schemas.users import UserCreate
from app.services.user_service import UserService

pytestmark = pytest.mark.unit


# Mock UserService
@pytest.fixture
def mock_user_service():
    return MagicMock(spec=UserService)


# Override dependency
@pytest.fixture(autouse=True)
def override_dependency(mock_user_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield
    app.dependency_overrides = {}


# Test client
@pytest.fixture
def client():
    return TestClient(app)


# Tests
def test_list_users(client, mock_user_service):
    """
    Test listing all users.
    """
    # Arrange
    mock_user_service.list_users.return_value = [
        User(
            id=1, username="Alice", gem_count=10, rank=0, balance=500.0, trade_count=0
        ),
        User(id=2, username="Bob", gem_count=15, rank=0, balance=300.0, trade_count=0),
    ]

    # Act
    response = client.get("/users/")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "username": "Alice",
            "gem_count": 10,
            "rank": 0,
            "balance": 500.0,
            "trade_count": 0,
        },
        {
            "id": 2,
            "username": "Bob",
            "gem_count": 15,
            "rank": 0,
            "balance": 300.0,
            "trade_count": 0,
        },
    ]
    mock_user_service.list_users.assert_called_once()


def test_create_user(client, mock_user_service):
    """
    Test creating a new user.
    """
    # Arrange
    user_data = {"username": "Alice"}
    created_user = User(
        id=1, username="Alice", gem_count=0, rank=0, balance=0.0, trade_count=0
    )
    mock_user_service.create_user.return_value = created_user

    # Act
    response = client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "gem_count": 0,
        "rank": 0,
        "balance": 0.0,
        "trade_count": 0,
    }
    mock_user_service.create_user.assert_called_once_with(UserCreate(**user_data))


def test_deposit_balance(client, mock_user_service):
    """
    Test depositing an amount into a user's balance.
    """
    user_id = 1
    deposit_data = {"user_id": user_id, "amount": 1000}

    response = client.post("/users/deposit", json=deposit_data)

    assert response.status_code == 204
    mock_user_service.deposit_balance.assert_called_once_with(user_id=1, amount=1000)


def test_withdraw_balance(client, mock_user_service):
    """
    Test withdrawing an amount from a user's balance.
    """
    user_id = 1
    withdraw_data = {"user_id": user_id, "amount": 1000}

    response = client.post("/users/withdraw", json=withdraw_data)

    assert response.status_code == 204
    mock_user_service.withdraw_balance.assert_called_once_with(user_id=1, amount=1000)


def test_create_user_conflict(client, mock_user_service):
    """
    Test creating a user that already exists.
    """
    # Arrange
    user_data = {"username": "Alice"}
    mock_user_service.create_user.side_effect = ValueError("Username already exists.")

    # Act
    response = client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists."}
    mock_user_service.create_user.assert_called_once_with(UserCreate(**user_data))


def test_get_user(client, mock_user_service):
    """
    Test retrieving a user by ID.
    """
    # Arrange
    user_id = 1
    user = User(
        id=1, username="Alice", gem_count=10, rank=0, balance=500.0, trade_count=0
    )
    mock_user_service.get_user.return_value = user

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "gem_count": 10,
        "rank": 0,
        "balance": 500.0,
        "trade_count": 0,
    }
    mock_user_service.get_user.assert_called_once_with(user_id)


def test_get_user_not_found(client, mock_user_service):
    """
    Test retrieving a non-existent user.
    """
    # Arrange
    user_id = 1
    mock_user_service.get_user.side_effect = ValueError("User not found.")

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
    mock_user_service.get_user.assert_called_once_with(user_id)
