# WebSocket Real-time Chat Skill

> Trigger: chat implementation, socket.io, real-time messaging, presence

## Client-Side (socket.io-client)

### Connection Setup
```jsx
import { io } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

const socket = io(WS_URL, {
  autoConnect: false,
  query: {
    token: localStorage.getItem('access_token'),
  },
});

// Connect when authenticated
socket.connect();

// Reconnection is handled automatically by socket.io-client
```

### Event Handlers
```jsx
// Join a chat room
socket.emit('join_room', { room_id: roomId });

// Send a message
socket.emit('send_message', { room_id: roomId, content: text });

// Listen for incoming messages
socket.on('message_received', (msg) => {
  // { id, room_id, sender_id, content, is_read, created_at }
  setMessages(prev => [...prev, msg]);
});

// Mark messages as read
socket.emit('mark_read', { room_id: roomId });

// Presence
socket.on('user_online', ({ user_id }) => { /* update UI */ });
socket.on('user_offline', ({ user_id }) => { /* update UI */ });
```

### React Hook Pattern
```jsx
import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

function useSocket(token) {
  const socketRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    socketRef.current = io(WS_URL, { query: { token } });

    return () => {
      socketRef.current?.disconnect();
    };
  }, [token]);

  return socketRef;
}
```

## Server-Side (python-socketio)

### Architecture
```
FastAPI app ←── socketio.ASGIApp(sio, other_app=app)
                    ↓
        python-socketio AsyncServer
                    ↓
        Event handlers (connect, send_message, join_room, etc.)
                    ↓
        ChatService → PostgreSQL (message persistence)
```

### Events Flow
```
1. Client connects with ?token=JWT
2. Server validates JWT in connect handler
3. Stores user_id in sio.session(sid)
4. Client emits join_room(room_id) → sio.enter_room()
5. Client emits send_message(room_id, content)
6. Server saves message via ChatService
7. Server emits message_received to room
8. Client emits mark_read(room_id) → bulk UPDATE is_read=true
```

## Key Rules
- JWT token as query param on connect: `?token=<access_token>`
- Message history loaded via REST: `GET /chats/{room_id}/messages`
- Real-time messages via WebSocket only
- Always save messages to DB before broadcasting
- Reconnection handled by socket.io-client automatically
