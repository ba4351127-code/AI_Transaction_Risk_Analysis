import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database.session import get_db
from backend.app.database.models.user_profile import User, UserBaseline
from backend.app.schemas.auth import (
    UserSignupRequest,
    UserLoginRequest,
    UserProfileResponse,
    TokenResponse
)
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user account with secure bcrypt hashing and generates a JWT access token.
    Never collects bank credentials, UPI PINs, OTPs, or card details.
    """
    normalized_email = payload.email.lower().strip()

    # Check for existing user with this email
    existing_user_query = await db.execute(
        select(User).where(User.email == normalized_email)
    )
    if existing_user_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in instead."
        )

    # Derive full name and user identifier
    full_name = payload.full_name.strip() if payload.full_name else normalized_email.split("@")[0].title()
    user_identifier = f"USR-{uuid.uuid4().hex[:6].upper()}"

    # Hash password with bcrypt
    hashed = hash_password(payload.password)
    now_utc = datetime.now(timezone.utc)

    new_user = User(
        user_identifier=user_identifier,
        email=normalized_email,
        full_name=full_name,
        hashed_password=hashed,
        is_active=True,
        role="user",
        created_at=now_utc
    )
    db.add(new_user)
    await db.flush()

    # Automatically initialize user behavioral risk baseline
    baseline = UserBaseline(
        user_id=new_user.id,
        avg_amount_30d=350.0,
        std_amount_30d=150.0,
        max_amount_recorded=1000.0,
        total_transactions_count=0,
        common_locations=[],
        known_device_hashes=[],
        usual_hour_distribution=list(range(8, 23))
    )
    db.add(baseline)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

    # Issue JWT Token without calling db.refresh() to avoid lazy loading IO
    token = create_access_token(data={
        "sub": new_user.id,
        "email": new_user.email,
        "name": new_user.full_name
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(
            id=new_user.id,
            user_identifier=new_user.user_identifier,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            created_at=new_user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates an existing user via email and password, issuing a JWT access token.
    """
    normalized_email = payload.email.lower().strip()

    user_query = await db.execute(
        select(User).where(User.email == normalized_email)
    )
    user = user_query.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support."
        )

    # Issue JWT Token
    token = create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "name": user.full_name
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(
            id=user.id,
            user_identifier=user.user_identifier,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the authenticated user's profile details.
    """
    return UserProfileResponse(
        id=current_user.id,
        user_identifier=current_user.user_identifier,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at
    )
