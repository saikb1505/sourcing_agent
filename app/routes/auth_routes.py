from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    TokenResponse,
    UserResponse,
    UserPasswordUpdate,
)
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    - **username**: User's username or email
    - **password**: User's password
    """
    user_repo = UserRepository(db)

    # Try to find user by username or email
    user = user_repo.get_by_username(form_data.username)
    if not user:
        user = user_repo.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return current_user


@router.put("/me/password")
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user_repo = UserRepository(db)
    user_repo.update_password(current_user.id, password_data.new_password)

    return {"message": "Password updated successfully"}
