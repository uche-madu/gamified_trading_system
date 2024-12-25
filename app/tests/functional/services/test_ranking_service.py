import logging

import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.functional


def test_update_user_gem_count(ranking_service, user_service):
    """Test updating a user's gem count."""
    # Arrange: Verify the initial gem count for user 1 (Alice)
    user = user_service.get_user(user_id=1)
    assert user.gem_count == 150

    # Act: Update gem count
    ranking_service.update_user_gem_count(user_id=1, gem_count=250)

    # Assert: Verify the updated gem count
    updated_user = user_service.get_user(user_id=1)
    assert updated_user.gem_count == 250


def test_assign_ranks(ranking_service, user_service):
    """Test assigning ranks to users based on gem count."""
    # Arrange: Verify initial ranks are None
    users = user_service.list_users()
    for user in users:
        assert user.rank == 0

    # Act: Call assign_ranks
    ranking_service.assign_ranks()

    # Assert: Verify ranks based on gem count
    ranked_users = user_service.list_users()

    assert ranked_users[2].rank == 1  # Charlie has the highest gem count (200)
    assert ranked_users[0].rank == 2  # Alice has the second-highest gem count (150)
    assert ranked_users[1].rank == 3  # Bob has the third-highest gem count (100)
    assert ranked_users[3].rank == 3  # Diana and Bob tie with 100 gems
    assert ranked_users[5].rank == 5  # Frank has the second lowest gem count (14)
    assert ranked_users[4].rank == 6  # Eve has the lowest gem count (4)


def test_get_top_n_users(ranking_service):
    """Test retrieving the top N users based on gem count."""
    # Act: Fetch the top 3 users
    top_users = ranking_service.get_top_n_users(n=3)

    # Assert: Verify the top users
    assert len(top_users) == 3
    assert top_users[0].username == "Charlie"  # Highest gem count (200)
    assert top_users[1].username == "Alice"  # Second highest gem count (150)
    assert top_users[2].username == "Bob"  # Third highest gem count (100)
