from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.users import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user in the database.
        """
        # Check if the user ID already exists
        existing_user = self.db.query(User).filter(User.id == user_data.user_id).first()
        if existing_user:
            raise ValueError("User ID already exists.")

        # Create a new user instance and add to the database
        user = User(id=user_data.user_id, username=user_data.username)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)  # Refresh to get updated fields (e.g., default values)
        return user

    def get_user(self, user_id: int) -> User:
        """
        Retrieve a user by their ID.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found.")
        return user

    def list_users(self) -> list[User]:
        """
        List all users in the database.
        """
        return self.db.query(User).all()

