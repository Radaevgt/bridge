import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime


class ChatParticipant(BaseModel):
    id: uuid.UUID
    full_name: str
    avatar_url: str | None = None


class ChatRoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    specialist_id: uuid.UUID
    created_at: datetime
    client: ChatParticipant | None = None
    specialist: ChatParticipant | None = None
    last_message: MessageResponse | None = None
    unread_count: int = 0


class SendMessageRequest(BaseModel):
    content: str
