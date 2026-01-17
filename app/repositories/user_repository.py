from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_admin=user_data.is_admin,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user details."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Update user password."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user account."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_active = False
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def activate(self, user_id: int) -> Optional[User]:
        """Activate a user account."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_active = True
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
