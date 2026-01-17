from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.repositories.user_repository import UserRepository
from app.repositories.search_query_repository import SearchQueryRepository
from app.repositories.search_result_repository import SearchResultRepository
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.schemas.search_schema import SearchQueryResponse
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# User Management Endpoints


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user (Admin only).

    This is the only way to create users in the system - no self-registration.
    """
    user_repo = UserRepository(db)

    # Check if email already exists
    if user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    new_user = user_repo.create(user_data)
    return new_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all users (Admin only)."""
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get a specific user by ID (Admin only)."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update user details (Admin only)."""
    user_repo = UserRepository(db)

    # Check user exists
    existing_user = user_repo.get_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check email uniqueness if being changed
    if user_data.email and user_data.email != existing_user.email:
        if user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Check username uniqueness if being changed
    if user_data.username and user_data.username != existing_user.username:
        if user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    updated_user = user_repo.update(user_id, user_data)
    return updated_user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Deactivate a user account (Admin only)."""
    user_repo = UserRepository(db)

    # Prevent admin from deactivating themselves
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user = user_repo.deactivate(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Activate a user account (Admin only)."""
    user_repo = UserRepository(db)

    user = user_repo.activate(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Reset a user's password (Admin only)."""
    user_repo = UserRepository(db)

    user = user_repo.update_password(user_id, new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "Password reset successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete a user (Admin only). Use with caution."""
    user_repo = UserRepository(db)

    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "User deleted successfully"}


# Search Query Management Endpoints


@router.get("/queries", response_model=List[SearchQueryResponse])
async def list_all_queries(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all search queries across all users (Admin only)."""
    query_repo = SearchQueryRepository(db)
    queries = query_repo.get_all(skip=skip, limit=limit)
    return queries


@router.get("/queries/user/{user_id}", response_model=List[SearchQueryResponse])
async def get_user_queries(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all search queries for a specific user (Admin only)."""
    query_repo = SearchQueryRepository(db)
    queries = query_repo.get_by_user(user_id, skip=skip, limit=limit)
    return queries


@router.delete("/queries/{query_id}")
async def admin_delete_query(
    query_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete any search query (Admin only)."""
    query_repo = SearchQueryRepository(db)

    if not query_repo.delete(query_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    return {"message": "Search query deleted successfully"}


# Statistics Endpoint


@router.get("/stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get system-wide statistics (Admin only)."""
    user_repo = UserRepository(db)
    query_repo = SearchQueryRepository(db)

    all_users = user_repo.get_all(limit=10000)
    all_queries = query_repo.get_all(limit=10000)

    active_users = sum(1 for u in all_users if u.is_active)
    admin_users = sum(1 for u in all_users if u.is_admin)

    return {
        "total_users": len(all_users),
        "active_users": active_users,
        "admin_users": admin_users,
        "total_search_queries": len(all_queries),
    }
