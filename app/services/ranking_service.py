from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.user import User


class RankingService:
    def __init__(self, db: Session):
        self.db = db

    def update_user_gem_count(self, user_id: int, gem_count: int):
        """
        Update the gem count of a user in the database.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found.")
        user.gem_count = gem_count
        self.db.commit()

    def assign_ranks(self):
        """
        Assign ranks to users in the database based on their gem counts.
        Handles ties by assigning the same rank to users with equal gem counts.
        """
        users = self.db.query(User).order_by(desc(User.gem_count)).all()
        rank = 1
        previous_gem_count = None

        for i, user in enumerate(users):
            # Assign the same rank for users with the same gem_count
            if user.gem_count != previous_gem_count:
                rank = i + 1  # Adjust rank only for different gem_count
            user.rank = rank
            previous_gem_count = user.gem_count

        self.db.commit()

    def get_top_n_users(self, n: int):
        """
        Get the top n users based on gem count, sorted in descending order
        by gem count and ascending order by user ID as tiebreaker.
        """
        top_users = (
            self.db.query(User)
            .order_by(desc(User.gem_count), asc(User.id))
            .limit(n)
            .all()
        )
        return top_users
