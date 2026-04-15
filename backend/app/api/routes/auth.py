from datetime import datetime, timedelta, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.session import Session
from app.models.user import ProfessionalProfile, User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut
from app.services.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db_session)):
    existing_stmt = select(User).where(User.email == payload.email)
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        role=payload.role,
    )
    db.add(user)
    await db.flush()

    if payload.role == "professional" and payload.professional_details:
        profile = ProfessionalProfile(
            user_id=user.id,
            specialization=payload.professional_details.specialization,
            bio=payload.professional_details.bio,
            price_per_session=payload.professional_details.price,
            availability=payload.professional_details.availability,
        )
        db.add(profile)

    session = Session(
        id=uuid.uuid4(),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.session_duration_hours),
    )
    db.add(session)
    await db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=str(session.id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite_normalized,
        max_age=settings.session_duration_hours * 3600,
    )

    return AuthResponse(user=UserOut(id=str(user.id), email=user.email, name=user.name, role=user.role))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db_session)):
    user_stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(user_stmt)).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session = Session(
        id=uuid.uuid4(),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.session_duration_hours),
    )
    db.add(session)
    await db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=str(session.id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite_normalized,
        max_age=settings.session_duration_hours * 3600,
    )

    return AuthResponse(user=UserOut(id=str(user.id), email=user.email, name=user.name, role=user.role))


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    delete_stmt = select(Session).where(Session.user_id == user.id)
    sessions = (await db.execute(delete_stmt)).scalars().all()
    for session in sessions:
        await db.delete(session)

    await db.commit()
    response.delete_cookie(settings.session_cookie_name)
    return {"success": True}


@router.get("/me", response_model=AuthResponse)
async def me(user: User = Depends(get_current_user)):
    return AuthResponse(user=UserOut(id=str(user.id), email=user.email, name=user.name, role=user.role))
