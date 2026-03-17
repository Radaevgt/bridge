import uuid

import socketio
from sqlalchemy import or_, select, update

from app.config import settings
from app.database import async_session
from app.models.chat import ChatRoom, Message
from app.services.chat_service import ChatService
from app.utils.jwt import decode_token

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins_list,
    logger=True,
    engineio_logger=True,
)


def _extract_token(environ: dict, auth: dict | None) -> str | None:
    """Try multiple strategies to extract JWT from the connect request."""
    # 1. Auth dict (socket.io-client v4+ with auth: { token })
    if auth and isinstance(auth, dict):
        token = auth.get("token")
        if token:
            return token

    # 2. Query string (socket.io-client with query: { token })
    query_string = environ.get("QUERY_STRING") or environ.get("query_string", b"")
    if isinstance(query_string, bytes):
        query_string = query_string.decode("utf-8")
    for param in query_string.split("&"):
        if param.startswith("token="):
            return param.split("=", 1)[1]

    # 3. ASGI scope headers (Authorization: Bearer <token>)
    headers = environ.get("headers", [])
    if isinstance(headers, list):
        for name, value in headers:
            header_name = name.decode("utf-8") if isinstance(name, bytes) else name
            if header_name.lower() == "authorization":
                header_val = value.decode("utf-8") if isinstance(value, bytes) else value
                if header_val.startswith("Bearer "):
                    return header_val[7:]

    return None


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None) -> bool:
    token = _extract_token(environ, auth)
    if not token:
        return False

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return False

    user_id = payload.get("sub")
    async with sio.session(sid) as session:
        session["user_id"] = user_id

    await sio.emit("user_online", {"user_id": user_id})
    return True


@sio.event
async def disconnect(sid: str) -> None:
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
    if user_id:
        await sio.emit("user_offline", {"user_id": user_id})


@sio.event
async def join_room(sid: str, data: dict) -> None:
    room_id = data.get("room_id")
    if not room_id:
        return

    async with sio.session(sid) as session:
        user_id = session.get("user_id")

    if not user_id:
        return

    # Verify user is a member of this room before allowing join
    async with async_session() as db:
        result = await db.execute(
            select(ChatRoom).where(
                ChatRoom.id == uuid.UUID(room_id),
                or_(
                    ChatRoom.client_id == uuid.UUID(user_id),
                    ChatRoom.specialist_id == uuid.UUID(user_id),
                ),
            )
        )
        room = result.scalar_one_or_none()

    if not room:
        return  # silently reject — user is not a member

    await sio.enter_room(sid, room_id)


@sio.event
async def send_message(sid: str, data: dict) -> None:
    room_id = data.get("room_id")
    content = data.get("content", "").strip()
    if not room_id or not content:
        return

    async with sio.session(sid) as session:
        user_id = session.get("user_id")

    if not user_id:
        return

    async with async_session() as db:
        service = ChatService(db)
        message = await service.save_message(
            room_id=uuid.UUID(room_id),
            sender_id=uuid.UUID(user_id),
            content=content,
        )

    await sio.emit(
        "message_received",
        {
            "id": str(message.id),
            "room_id": str(message.room_id),
            "sender_id": str(message.sender_id),
            "content": message.content,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat(),
        },
        room=room_id,
    )


@sio.event
async def mark_read(sid: str, data: dict) -> None:
    room_id = data.get("room_id")
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
    if not room_id or not user_id:
        return

    async with async_session() as db:
        await db.execute(
            update(Message)
            .where(
                Message.room_id == uuid.UUID(room_id),
                Message.sender_id != uuid.UUID(user_id),
            )
            .values(is_read=True)
        )
        await db.commit()
