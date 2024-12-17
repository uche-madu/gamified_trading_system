from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_user_service
from app.main import app
from app.models.user import User
from app.schemas.users import UserCreate
from app.services.user_service import UserService


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
        User(id=1, username="Alice", gem_count=10, rank=None),
        User(id=2, username="Bob", gem_count=15, rank=None),
    ]

    # Act
    response = client.get("/users/")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "username": "Alice", "gem_count": 10, "rank": None},
        {"id": 2, "username": "Bob", "gem_count": 15, "rank": None},
    ]
    mock_user_service.list_users.assert_called_once()


def test_create_user(client, mock_user_service):
    """
    Test creating a new user.
    """
    # Arrange
    user_data = {"user_id": 1, "username": "Alice"}
    created_user = User(id=1, username="Alice", gem_count=0, rank=None)
    mock_user_service.create_user.return_value = created_user

    # Act
    response = client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "gem_count": 0,
        "rank": None,
    }
    mock_user_service.create_user.assert_called_once_with(UserCreate(**user_data))


def test_get_user(client, mock_user_service):
    """
    Test retrieving a user by ID.
    """
    # Arrange
    user_id = 1
    user = User(id=1, username="Alice", gem_count=10, rank=None)
    mock_user_service.get_user.return_value = user

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "gem_count": 10,
        "rank": None,
    }
    mock_user_service.get_user.assert_called_once_with(user_id)


def test_create_user_conflict(client, mock_user_service):
    """
    Test creating a user that already exists.
    """
    # Arrange
    user_data = {"user_id": 1, "username": "Alice"}
    mock_user_service.create_user.side_effect = ValueError("User ID already exists.")

    # Act
    response = client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "User ID already exists."}
    mock_user_service.create_user.assert_called_once_with(UserCreate(**user_data))


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
