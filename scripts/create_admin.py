#!/usr/bin/env python3
"""
Script to create the initial admin user.
Run this after setting up the database.

Usage:
    python scripts/create_admin.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate


def create_admin_user(
    email: str = "admin@example.com",
    username: str = "admin",
    password: str = "admin123",
    full_name: str = "System Administrator",
):
    """Create an admin user."""
    # Initialize database tables
    init_db()

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)

        # Check if admin already exists
        existing_user = user_repo.get_by_email(email)
        if existing_user:
            print(f"User with email {email} already exists.")
            return existing_user

        existing_user = user_repo.get_by_username(username)
        if existing_user:
            print(f"User with username {username} already exists.")
            return existing_user

        # Create admin user
        admin_data = UserCreate(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            is_admin=True,
        )

        admin_user = user_repo.create(admin_data)
        print(f"Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print("\nPlease change the password after first login.")
        return admin_user

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument(
        "--full-name", default="System Administrator", help="Admin full name"
    )

    args = parser.parse_args()

    create_admin_user(
        email=args.email,
        username=args.username,
        password=args.password,
        full_name=args.full_name,
    )
