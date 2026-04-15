from datetime import datetime, timezone
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.session import Session
from app.models.user import User


async def get_current_user(
    session_id: str | None = Cookie(default=None, alias=get_settings().session_cookie_name),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        session_uuid = UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    session_stmt = select(Session).where(Session.id == session_uuid)
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()

    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user_stmt = select(User).where(User.id == session.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
