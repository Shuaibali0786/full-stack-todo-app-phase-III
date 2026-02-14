import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.models.user import User, UserBase
from src.services.auth_service import AuthService
from src.api.deps import get_current_user
from src.core.database import get_session
from src.core.security import verify_token, hash_password
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str


@router.post("/login")
async def login(login_request: LoginRequest, session: AsyncSession = Depends(get_session)):
    """
    Authenticate user and return access/refresh tokens
    """
    result = await AuthService.authenticate_user(
        session, login_request.email, login_request.password
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, access_token, refresh_token = result

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }


@router.post("/register")
async def register(register_request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """
    Register a new user
    """
    user_data = UserBase(
        email=register_request.email,
        first_name=register_request.first_name,
        last_name=register_request.last_name
    )

    try:
        # Register the user but don't return tokens (per spec clarification 2026-01-17)
        # User must manually login after registration - don't auto-login
        user = await AuthService.register_user_no_tokens(
            session, user_data, register_request.password
        )

        return {
            "message": "User registered successfully",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError as e:
        # DB-level unique constraint violation (race condition on duplicate email)
        logger.error(f"Integrity error during registration: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error during registration: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.post("/logout")
async def logout():
    """
    Log out the current user
    """
    # In a real implementation, you might invalidate the token
    await AuthService.logout_user(None)
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh(refresh_request: RefreshRequest, session: AsyncSession = Depends(get_session)):
    """
    Refresh access token using refresh token
    """
    result = await AuthService.refresh_access_token(session, refresh_request.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = result
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Reset password directly — accepts email + new_password.
    No email sending required: finds user, hashes new password, saves to DB.
    """
    if not request.new_password or len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )

    try:
        # Find user by email
        result = await session.exec(select(User).where(User.email == request.email))
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with that email address"
            )

        # Hash new password and update user record
        user.hashed_password = hash_password(request.new_password)
        user.updated_at = datetime.utcnow()
        session.add(user)
        await session.commit()

        return {"message": "Password updated successfully"}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )