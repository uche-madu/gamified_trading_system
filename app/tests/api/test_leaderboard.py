import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.models.user import User
from app.dependencies import get_ranking_service

client = TestClient(app)

@pytest.fixture
def mock_ranking_service():
    """Fixture for Mock RankingService."""
    return MagicMock()

@pytest.fixture(autouse=True)
def override_ranking_service(mock_ranking_service):
    """
    Override the TradeService dependency with the mock.
    """
    app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
    yield
    app.dependency_overrides.clear()


def test_get_leaderboard(mock_ranking_service):
    """
    Test retrieving the leaderboard with top users.
    """
    # Arrange: Mock users
    mock_users = [
        User(rank=1, username="Alice", gem_count=50),
        User(rank=2, username="Bob", gem_count=40),
        User(rank=3, username="Charlie", gem_count=30),
    ]
    mock_ranking_service.get_top_n_users.return_value = mock_users

    # Act: Call the endpoint
    response = client.get("/leaderboard/?top_n=3")

    # Assertions
    assert response.status_code == 200
    assert response.json() == [
        {"rank": 1, "username": "Alice", "gem_count": 50},
        {"rank": 2, "username": "Bob", "gem_count": 40},
        {"rank": 3, "username": "Charlie", "gem_count": 30},
    ]
    mock_ranking_service.assign_ranks.assert_called_once()
    mock_ranking_service.get_top_n_users.assert_called_once_with(3)
