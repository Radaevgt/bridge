import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatRoom, Message
from app.schemas.chat import ChatParticipant, ChatRoomResponse, MessageResponse


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_rooms(self, user_id: uuid.UUID) -> list[ChatRoomResponse]:
        result = await self.db.execute(
            select(ChatRoom)
            .where(
                or_(ChatRoom.client_id == user_id, ChatRoom.specialist_id == user_id)
            )
            .options(
                selectinload(ChatRoom.client),
                selectinload(ChatRoom.specialist),
            )
            .order_by(ChatRoom.created_at.desc())
        )
        rooms = list(result.scalars().all())

        response: list[ChatRoomResponse] = []
        for room in rooms:
            # Get last message for this room
            last_msg_result = await self.db.execute(
                select(Message)
                .where(Message.room_id == room.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_msg = last_msg_result.scalar_one_or_none()

            # Count unread messages (messages NOT sent by current user and not read)
            unread_result = await self.db.execute(
                select(func.count(Message.id)).where(
                    Message.room_id == room.id,
                    Message.sender_id != user_id,
                    Message.is_read.is_(False),
                )
            )
            unread_count = unread_result.scalar() or 0

            response.append(
                ChatRoomResponse(
                    id=room.id,
                    client_id=room.client_id,
                    specialist_id=room.specialist_id,
                    created_at=room.created_at,
                    client=ChatParticipant(
                        id=room.client.id,
                        full_name=room.client.full_name,
                        avatar_url=room.client.avatar_url,
                    ),
                    specialist=ChatParticipant(
                        id=room.specialist.id,
                        full_name=room.specialist.full_name,
                        avatar_url=room.specialist.avatar_url,
                    ),
                    last_message=MessageResponse.model_validate(last_msg)
                    if last_msg
                    else None,
                    unread_count=unread_count,
                )
            )

        return response

    async def get_messages(
        self, room_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Message]:
        # Verify user is a member of this room
        result = await self.db.execute(
            select(ChatRoom).where(
                ChatRoom.id == room_id,
                or_(ChatRoom.client_id == user_id, ChatRoom.specialist_id == user_id),
            )
        )
        room = result.scalar_one_or_none()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this chat",
            )

        result = await self.db.execute(
            select(Message)
            .where(Message.room_id == room_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_room(
        self, client_id: uuid.UUID, specialist_id: uuid.UUID
    ) -> ChatRoom:
        # Check if room already exists
        result = await self.db.execute(
            select(ChatRoom).where(
                ChatRoom.client_id == client_id,
                ChatRoom.specialist_id == specialist_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        room = ChatRoom(client_id=client_id, specialist_id=specialist_id)
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def save_message(
        self, room_id: uuid.UUID, sender_id: uuid.UUID, content: str
    ) -> Message:
        message = Message(room_id=room_id, sender_id=sender_id, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
