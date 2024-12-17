from app.models import User


def test_update_user_gem_count(ranking_service, db_session, users):
    """Test updating a user's gem count."""
    # Arrange: Verify the initial gem count for user 1 (Alice)
    alice = db_session.query(User).filter(User.id == 1).first()
    assert alice.gem_count == 15

    # Act: Update gem count
    ranking_service.update_user_gem_count(user_id=1, gem_count=25)

    # Assert: Verify the updated gem count
    updated_alice = db_session.query(User).filter(User.id == 1).first()
    assert updated_alice.gem_count == 25


def test_assign_ranks(ranking_service, db_session, users):
    """Test assigning ranks to users based on gem count."""
    # Arrange: Verify initial ranks are None
    for user in users:
        assert user.rank is None

    # Act: Call assign_ranks
    ranking_service.assign_ranks()

    # Assert: Verify ranks based on gem count
    charlie = db_session.query(User).filter(User.username == "Charlie").first()
    alice = db_session.query(User).filter(User.username == "Alice").first()
    bob = db_session.query(User).filter(User.username == "Bob").first()
    diana = db_session.query(User).filter(User.username == "Diana").first()

    assert charlie.rank == 1  # Charlie has the highest gem count (20)
    assert alice.rank == 2  # Alice has the second-highest gem count (15)
    assert bob.rank == 3  # Bob and Diana tie with 10 gems
    assert diana.rank == 3


def test_get_top_n_users(ranking_service, db_session, users):
    """Test retrieving the top N users based on gem count."""
    # Act: Fetch the top 2 users
    top_users = ranking_service.get_top_n_users(n=2)

    # Assert: Verify the top users
    assert len(top_users) == 2
    assert top_users[0].username == "Charlie"  # Highest gem count (20)
    assert top_users[1].username == "Alice"  # Second highest gem count (15)
