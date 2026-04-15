from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.chat import Chat, Message
from app.models.user import ProfessionalProfile, User
from app.schemas.chat import ChatRequest, SaveMessageRequest
from app.services.agent import get_agent_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    profiles_stmt = (
        select(User.name, ProfessionalProfile.specialization, ProfessionalProfile.price_per_session, ProfessionalProfile.availability)
        .join(ProfessionalProfile, ProfessionalProfile.user_id == User.id)
        .where(User.role == "professional")
    )
    rows = (await db.execute(profiles_stmt)).all()
    professionals = [
        {
            "name": row.name,
            "specialization": row.specialization,
            "price_per_session": float(row.price_per_session) if row.price_per_session else None,
            "availability": row.availability,
        }
        for row in rows
    ]

    _ = user
    result = await get_agent_service().process_chat(payload.messages, payload.language, professionals)
    return result


@router.post("/messages")
async def save_message(
    payload: SaveMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        chat_uuid = UUID(payload.chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat id") from exc

    chat_stmt = select(Chat).where(Chat.id == chat_uuid)
    chat = (await db.execute(chat_stmt)).scalar_one_or_none()

    if chat is None:
        chat = Chat(id=chat_uuid, user_id=str(user.id))
        db.add(chat)
    elif chat.user_id != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    message = Message(
        chat_id=chat_uuid,
        role=payload.role,
        content=payload.content,
        risk_level=payload.risk_level,
        language=payload.language,
    )
    db.add(message)
    await db.commit()

    return {"success": True}


@router.get("/chats")
async def list_chats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    chats_stmt = select(Chat).where(Chat.user_id == str(user.id)).order_by(desc(Chat.created_at))
    chats = (await db.execute(chats_stmt)).scalars().all()
    return {
        "chats": [
            {
                "id": str(chat.id),
                "user_id": chat.user_id,
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
            }
            for chat in chats
        ]
    }


@router.get("/chats/{chat_id}/messages")
async def list_messages(chat_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    try:
        chat_uuid = UUID(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat id") from exc

    chat_stmt = select(Chat).where(Chat.id == chat_uuid)
    chat = (await db.execute(chat_stmt)).scalar_one_or_none()

    if not chat or chat.user_id != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    messages_stmt = select(Message).where(Message.chat_id == chat_uuid).order_by(Message.created_at.asc())
    messages = (await db.execute(messages_stmt)).scalars().all()

    return {
        "messages": [
            {
                "id": str(message.id),
                "chat_id": str(message.chat_id),
                "role": message.role,
                "content": message.content,
                "risk_level": message.risk_level,
                "language": message.language,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ]
    }
