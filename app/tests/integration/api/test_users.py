import pytest
from fastapi.testclient import TestClient
from services.user_service import UserService

from app.main import app

client = TestClient(app)

pytestmark = pytest.mark.integration


def test_list_users(postgres_db_session, postgres_users):
    """
    Test listing all users.
    """
    # Act
    response = client.get("/users/")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "username": "Alice",
            "gem_count": 150,
            "rank": 0,
            "balance": 500.0,
            "trade_count": 0,
        },
        {
            "id": 2,
            "username": "Bob",
            "gem_count": 100,
            "rank": 0,
            "balance": 1000.0,
            "trade_count": 0,
        },
        {
            "id": 3,
            "username": "Charlie",
            "gem_count": 200,
            "rank": 0,
            "balance": 300.0,
            "trade_count": 0,
        },
        {
            "id": 4,
            "username": "Diana",
            "gem_count": 100,
            "rank": 0,
            "balance": 200.0,
            "trade_count": 0,
        },
        {
            "id": 5,
            "username": "Eve",
            "gem_count": 4,
            "rank": 0,
            "balance": 2000.0,
            "trade_count": 4,
        },
        {
            "id": 6,
            "username": "Frank",
            "gem_count": 14,
            "rank": 0,
            "balance": 1500.0,
            "trade_count": 9,
        },
    ]


def test_create_user(postgres_db_session):
    """
    Test creating a new user.
    """
    # Arrange
    user_data = {"username": "Eve"}
    response = client.post("/users/", json=user_data)

    # Act: Query the database for the created user
    user_service = UserService(postgres_db_session)
    created_user = user_service.get_user(user_id=1)

    # Assert
    assert response.status_code == 201
    assert created_user is not None
    assert created_user.username == "Eve"
    assert created_user.gem_count == 0
    assert created_user.balance == 0.0


def test_deposit_balance(postgres_db_session, postgres_users):
    """
    Test depositing an amount into a user"s balance.
    """
    # Arrange
    user_service = UserService(postgres_db_session)
    user = user_service.get_user(user_id=1)
    deposit_data = {"user_id": user.id, "amount": 1000}

    # Act
    response = client.post("/users/deposit", json=deposit_data)

    # Assert
    assert response.status_code == 204
    updated_user = user_service.get_user(user_id=user.id)
    assert updated_user.balance == 1500.0  # Original balance (500.0) + 1000


def test_withdraw_balance(postgres_db_session, postgres_users):
    """
    Test withdrawing an amount from a user"s balance.
    """
    # Arrange
    user_service = UserService(postgres_db_session)
    user = user_service.get_user(user_id=1)

    withdraw_data = {"user_id": user.id, "amount": 200}

    # Act
    response = client.post("/users/withdraw", json=withdraw_data)

    # Assert
    assert response.status_code == 204
    updated_user = user_service.get_user(user_id=user.id)
    assert updated_user.balance == 300.0  # Original balance (500.0) - 200


def test_create_user_conflict(postgres_db_session, postgres_users):
    """
    Test creating a user that already exists.
    """
    # Arrange
    user_data = {"username": "Alice"}

    # Act
    response = client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists."}


def test_get_user(postgres_db_session, postgres_users):
    """
    Test retrieving a user by ID.
    """
    # Arrange
    user_id = 1

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "gem_count": 150,
        "rank": 0,
        "balance": 500.0,
        "trade_count": 0,
    }


def test_get_user_not_found(postgres_db_session):
    """
    Test retrieving a non-existent user.
    """
    # Arrange
    user_id = 9999  # Non-existent user

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
