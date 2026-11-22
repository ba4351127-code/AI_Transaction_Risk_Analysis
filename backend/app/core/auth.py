from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db
from backend.app.database.models.user_profile import User
from backend.app.core.security import decode_access_token

http_bearer = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Extracts the authenticated User if an Authorization: Bearer token is provided and valid.
    If no token is supplied or if it is invalid, returns None without raising an exception.
    Enables dual-mode support for public/demo endpoints and automated testing suites.
    """
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    query = await db.execute(
        select(User)
        .options(selectinload(User.baseline))
        .where(User.id == user_id, User.is_active.is_(True))
    )
    user = query.scalar_one_or_none()
    return user


async def get_current_user(
    user: Optional[User] = Depends(get_optional_current_user)
) -> User:
    """
    Enforces required authentication. Raises HTTP 401 Unauthorized if the user is not authenticated.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in or provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
