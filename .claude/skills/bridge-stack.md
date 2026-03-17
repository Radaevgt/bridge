# Bridge Stack Architecture Skill

> Trigger: questions about data flow, API integration, layer interactions, "how does X connect to Y"

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  React SPA (Vite + Tailwind + Zustand)          │
│  Port: 5173 (dev) / 3000 (Docker)              │
│                                                  │
│  State: Zustand (auth, chat unread)             │
│  Server state: TanStack Query v5                │
│  Forms: React Hook Form + Zod                   │
│  HTTP: Axios with interceptors                  │
│  WebSocket: socket.io-client                    │
└──────────────┬──────────────┬───────────────────┘
               │ REST (JSON)  │ WebSocket
               ▼              ▼
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (Python 3.11, async)           │
│  Port: 8000                                     │
│                                                  │
│  Auth: JWT (access 30min + refresh 7d)          │
│  Passwords: bcrypt via passlib                   │
│  Validation: Pydantic v2                        │
│  WebSocket: python-socketio (ASGI)              │
│                                                  │
│  Pattern: Router → Service → Repository → DB    │
└──────────────┬──────────────┬───────────────────┘
               │ SQLAlchemy   │ Pub/Sub
               │ 2.0 async    │
               ▼              ▼
┌──────────────────────┐ ┌────────────────────────┐
│  PostgreSQL 15       │ │  Redis 7               │
│  Primary data store  │ │  WebSocket pub/sub     │
│  UUID primary keys   │ │  Session cache         │
└──────────────────────┘ └────────────────────────┘
```

## Data Flow Examples

### User Registration
```
React form (React Hook Form + Zod validation)
  → POST /auth/register (Axios)
  → routers/auth.py → services/auth_service.py
  → hash password (bcrypt) → save to PostgreSQL
  → generate JWT tokens → return to client
  → Zustand authStore saves tokens to localStorage
```

### Specialist Search
```
React Search page (TanStack Query)
  → GET /specialists/?search=AI&domain=ML&sort=rating (Axios)
  → routers/specialists.py → services/specialist_service.py
  → SQLAlchemy async query with JOIN + WHERE + ORDER BY
  → Paginated response (12 per page)
  → TanStack Query caches results
```

### Real-time Chat
```
React connects socket.io-client with ?token=JWT
  → python-socketio validates JWT on connect
  → join_room(room_id) → sio.enter_room()
  → send_message(room_id, content)
  → ChatService saves to PostgreSQL
  → sio.emit("message_received") to room members
  → React updates chat UI in real-time
```

### Leave a Review
```
React form → POST /reviews/{specialist_id}
  → require_client dependency checks role
  → ReviewService checks UNIQUE(specialist_id, client_id)
  → Saves review + recalculates avg_rating on specialist_profiles
  → Returns 201 Created
```

## Key Conventions

- **ALL DB operations are async** — never use sync SQLAlchemy
- **Repository pattern**: routes → services → repositories → DB
- **Pydantic v2**: use `model_config = ConfigDict(from_attributes=True)`
- **Type hints on every Python function**
- **Tailwind only** in frontend — no custom CSS, no inline styles
- **English only** in all UI strings
- **UUID primary keys** everywhere
- **No payments** — Bridge only connects people
