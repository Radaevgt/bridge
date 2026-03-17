import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatRoom, Message
from app.models.user import User, UserRole
from app.schemas.chat import ChatRoomResponse, MessageResponse
from app.services.chat_service import ChatService
from app.utils.deps import get_current_user

router = APIRouter(prefix="/chats", tags=["chats"])


class CreateChatRequest(BaseModel):
    specialist_id: uuid.UUID


class SendMessageRequest(BaseModel):
    content: str


@router.post("/", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: CreateChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatRoomResponse:
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can start chats",
        )
    service = ChatService(db)
    room = await service.create_room(current_user.id, data.specialist_id)
    # Return full room with participants
    rooms = await service.get_user_rooms(current_user.id)
    for r in rooms:
        if r.id == room.id:
            return r
    return room


@router.get("/", response_model=list[ChatRoomResponse])
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatRoomResponse]:
    service = ChatService(db)
    return await service.get_user_rooms(current_user.id)


@router.get("/{room_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MessageResponse]:
    service = ChatService(db)
    return await service.get_messages(room_id, current_user.id)


@router.post(
    "/{room_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    room_id: uuid.UUID,
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """REST fallback for sending messages when WebSocket is unavailable."""
    service = ChatService(db)
    # Verify membership
    await service.get_messages(room_id, current_user.id)
    message = await service.save_message(room_id, current_user.id, data.content)
    return message


@router.patch("/{room_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_messages_read(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Mark all messages in a room as read (except own messages)."""
    # Verify membership
    service = ChatService(db)
    await service.get_messages(room_id, current_user.id)
    # Mark as read
    await db.execute(
        update(Message)
        .where(
            Message.room_id == room_id,
            Message.sender_id != current_user.id,
            Message.is_read == False,
        )
        .values(is_read=True)
    )
    await db.commit()
