from fastapi import Depends, HTTPException, status, Query, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.core.database import get_session
from src.core.security import verify_token
from src.models.user import User
from typing import AsyncGenerator, Optional
from fastapi.security import OAuth2PasswordBearer


# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    """
    Dependency to get the current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    statement = select(User).where(User.email == username)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception
    return user


async def get_current_user_sse(
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: Optional[str] = Query(None, description="JWT token for SSE authentication")
):
    """
    Dependency to get the current authenticated user for SSE endpoints.

    Supports token from either:
    1. Query parameter (?token=...) - for EventSource compatibility
    2. Authorization header (Bearer ...) - fallback

    This is needed because EventSource (used for SSE) doesn't support
    custom headers, so we pass token as query parameter.
    """
    # Try to get token from query parameter first (SSE use case)
    auth_token = token

    # Fallback to Authorization header if query param not provided
    if not auth_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.replace("Bearer ", "")

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide token in query parameter or Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(auth_token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    statement = select(User).where(User.email == username)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception
    return user