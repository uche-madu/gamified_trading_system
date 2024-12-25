import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ranking_service import RankingService

client = TestClient(app)


@pytest.mark.integration
def test_get_leaderboard(postgres_db_session, postgres_users):
    """
    Test retrieving the full leaderboard with actual data using PostgreSQL.
    """

    # Arrange
    ranking_service = RankingService(postgres_db_session)
    ranking_service.assign_ranks()

    # Act: Call the leaderboard endpoint
    response = client.get("/leaderboard/?top_n=3")  # Fetch all 3 users

    # Assert: Verify the response contains all 3 users in the correct order
    assert response.status_code == 200
    assert response.json() == [
        {"rank": 1, "username": "Charlie", "gem_count": 200},
        {"rank": 2, "username": "Alice", "gem_count": 150},
        {"rank": 3, "username": "Bob", "gem_count": 100},
    ]

    assert len(response.json()) == 3
    assert response.json()[0]["rank"] == 1
    assert response.json()[0]["username"] == "Charlie"
    assert (
        response.json()[2]["username"] != "Diana"
    )  # Leaderboard breaks ties by ordering by ID ASC
    assert response.json()[2]["username"] == "Bob"
