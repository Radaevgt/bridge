# CLAUDE.md — Bridge Project

> Expert Marketplace Platform · React + FastAPI + PostgreSQL + WebSocket

---

## 🗂 What is Bridge?

Bridge is a two-sided marketplace connecting **Clients** (people with tasks) and **Specialists** (experts: professors, consultants, mentors). The platform:
- Lets specialists build profile cards with competency proofs (links, certificates, publications)
- Lets clients search/filter specialists by domain, price, language, rating
- Connects both parties via real-time WebSocket chat
- Generates AI-powered lesson plans from chat conversations (Claude API)
- Smart matching: multi-criteria scoring with domain affinity, text matching, budget fit
- Does NOT process payments — Bridge only introduces people

**UI language: English only.** No Russian or other languages in any UI string, label, placeholder, error, or toast.

---

## 🏗 Architecture Overview

```
Client (React SPA)
    ↓ REST (Axios) + WebSocket (Socket.io-client)
FastAPI Backend (Python 3.11, async)
    ↓ SQLAlchemy 2.0 async ORM
PostgreSQL 15 (primary data)
    ↓ Redis (WebSocket pub/sub + session cache)
    ↓ Anthropic Claude API (AI lesson plans)
```

Two repos in one monorepo:
- `bridge-frontend/` — React 18, Vite, Tailwind CSS, Zustand, React Query
- `bridge-backend/` — FastAPI, SQLAlchemy 2.0 async, Alembic, python-socketio

---

## 🖥 Frontend Stack

| Technology | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| Vite | latest | Build tool / dev server |
| React Router | v6 | Client-side routing |
| Tailwind CSS | v3 | Styling — white/blue design |
| Zustand | latest | Global state (auth, chat unread) |
| TanStack Query | v5 | Server state, caching, pagination |
| Axios | latest | HTTP client |
| Socket.io-client | latest | WebSocket real-time chat |
| React Hook Form | latest | Form handling |
| Zod | latest | Schema validation |

### Frontend conventions
- **No custom CSS** — Tailwind classes only
- **No inline styles** — no `style={{}}` unless absolutely unavoidable
- Components live in `src/components/ComponentName/index.jsx`
- Pages live in `src/pages/PageName/index.jsx`
- API calls live in `src/api/` — one file per resource (auth.js, specialists.js, chats.js)
- Zustand stores in `src/store/` — authStore.js, chatStore.js
- Every form: loading state + error state + success toast
- Loading skeletons (not spinners) for list/search results
- Empty states must have helpful text + CTA button

### Color tokens (use EXACTLY these)
```
Primary:        #1A56DB   (buttons, links, active states)
Primary light:  #EBF2FF   (card backgrounds, badges)
Primary dark:   #1E3A5F   (headings, important text)
White:          #FFFFFF   (page bg, cards)
Gray-50:        #F9FAFB   (subtle section bg)
Text primary:   #111827   (body text)
Text secondary: #6B7280   (labels, hints, meta)
Border:         #E5E7EB   (dividers, card borders)
Error:          #EF4444   (validation errors)
Success:        #10B981   (available badge, success)
```

### Routes
```
/                   Landing page (public)
/login              Login form (public)
/register           Registration — choose role (public)
/search             Search + filters + results (public, full features need login)
/specialists/:id    Specialist public profile (public)
/dashboard          Client dashboard (client only)
/dashboard/specialist  Specialist dashboard (specialist only)
/chats              Inbox — conversation list (authenticated)
/chats/:roomId      Chat window (authenticated)
/settings           Account settings (authenticated)
/create-request     Task request wizard — 4 steps (client only)
```

---

## ⚙️ Backend Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime |
| FastAPI | latest | REST API + WebSocket |
| SQLAlchemy | 2.0 async | ORM |
| Alembic | latest | DB migrations |
| PostgreSQL | 15 | Primary database |
| Redis | 7 | WebSocket pub/sub, cache |
| python-socketio | latest | Socket.io server |
| Pydantic | v2 | Schemas + validation |
| passlib + bcrypt | latest | Password hashing |
| python-jose | latest | JWT tokens |
| httpx | latest | HTTP client for Claude API |

### Backend conventions
- **All DB calls must be async** — no sync SQLAlchemy anywhere
- **Repository pattern** — `services/` calls `repositories/`, routes call `services/`
- **Pydantic v2** for all request/response schemas — use `model_config = ConfigDict(...)`
- **Type hints on every function** — no untyped functions
- All endpoints return proper HTTP status codes (201 for creation, 204 for delete, 422 for validation)
- All error messages in English
- Passwords: never stored plain, always bcrypt
- JWT: access token (30 min) + refresh token (7 days)

### Backend file structure
```
bridge-backend/
├── app/
│   ├── main.py              # FastAPI app + CORS + routers + socketio mount
│   ├── config.py            # Pydantic Settings (reads .env), includes ANTHROPIC_API_KEY
│   ├── database.py          # Async SQLAlchemy engine + get_db dependency
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── specialist.py
│   │   ├── review.py
│   │   ├── chat.py
│   │   ├── task_request.py  # TaskRequest + TaskProposal
│   │   └── lesson_plan.py   # AI-generated lesson plans
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── specialist.py    # includes relevance_score field
│   │   ├── review.py
│   │   ├── chat.py
│   │   ├── task_request.py
│   │   └── lesson_plan.py
│   ├── routers/             # FastAPI routers
│   │   ├── auth.py
│   │   ├── specialists.py   # includes avatar upload
│   │   ├── reviews.py
│   │   ├── chats.py
│   │   ├── users.py
│   │   ├── task_requests.py
│   │   └── lesson_plans.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── specialist_service.py    # search with domain affinity
│   │   ├── review_service.py
│   │   ├── chat_service.py
│   │   ├── task_request_service.py  # smart matching with scoring
│   │   └── lesson_plan_service.py   # Claude API integration
│   ├── socket/              # Socket.io event handlers
│   │   └── chat_handlers.py
│   └── utils/
│       ├── jwt.py           # Token create/verify
│       ├── security.py      # Password hash/verify
│       ├── deps.py          # FastAPI dependencies (current_user, db)
│       ├── domain_affinity.py  # Domain relationship map + scoring helpers
│       └── scoring.py          # Multi-criteria relevance scoring
├── alembic/
│   └── versions/
├── scripts/
│   └── seed.py              # Demo data seeder (25 specialists, 10 clients)
├── tests/
│   ├── conftest.py          # Test fixtures (DB, client, auth helpers)
│   ├── test_auth.py         # 9 auth tests
│   ├── test_specialists.py  # 4 specialist tests
│   ├── test_chats.py        # 5 chat tests
│   ├── test_lesson_plans.py # 4 lesson plan tests (mocked Claude API)
│   └── test_load.py         # Concurrent load tests
├── media/avatars/           # Uploaded specialist photos
├── requirements.txt
├── .env.example
├── Dockerfile
├── railway.json
└── pytest.ini               # asyncio_mode = auto
```

### API endpoints
```
POST   /auth/register                   Public
POST   /auth/login                      Public
POST   /auth/refresh                    Refresh token

GET    /specialists/                    Search + filter (public) — domain affinity expansion
GET    /specialists/{id}                Get profile (public)
GET    /specialists/me                  My profile (specialist only)
POST   /specialists/profile             Create/update own card (specialist)
POST   /specialists/competencies        Add proof link (specialist)
DELETE /specialists/competencies/{id}   Remove link (specialist)
PATCH  /specialists/availability        Toggle status (specialist)
POST   /specialists/avatar              Upload photo (specialist)

POST   /reviews/{specialist_id}         Leave review (client only)
GET    /reviews/{specialist_id}         List reviews (public)

GET    /chats/                          My conversations (authenticated)
POST   /chats/                          Create chat room (client only)
GET    /chats/{room_id}/messages        Chat history (authenticated)
POST   /chats/{room_id}/messages        Send message REST (authenticated)
PATCH  /chats/{room_id}/read            Mark read (authenticated)

POST   /requests/                       Create task request (client)
GET    /requests/                       List requests (role-based)
GET    /requests/{id}                   Request detail (authenticated)
GET    /requests/{id}/specialists       Matching specialists with scores (client)
POST   /requests/{id}/proposals         Submit proposal (specialist)
PATCH  /requests/{id}/status            Update status (client)

POST   /lesson-plans/generate           Generate AI lesson plan (specialist)
GET    /lesson-plans/room/{room_id}     Get room's lesson plans (authenticated)

GET    /users/me                        My profile (authenticated)
PATCH  /users/me                        Update settings (authenticated)

WS     /ws/chat/{room_id}              Real-time chat (authenticated)
```

---

## 🗄 Database Schema

### users
```sql
id            UUID PRIMARY KEY
email         VARCHAR UNIQUE NOT NULL
password_hash VARCHAR NOT NULL
role          ENUM('client', 'specialist') NOT NULL
full_name     VARCHAR NOT NULL
avatar_url    VARCHAR
created_at    TIMESTAMP DEFAULT now()
updated_at    TIMESTAMP DEFAULT now()
```

### specialist_profiles
```sql
id            UUID PRIMARY KEY
user_id       UUID FK → users(id) UNIQUE
headline      VARCHAR(200)
bio           TEXT
hourly_rate   DECIMAL(10,2)
availability  ENUM('available', 'busy', 'vacation') DEFAULT 'available'
avg_rating    FLOAT DEFAULT 0
review_count  INTEGER DEFAULT 0
```

### specialist_domains
```sql
id              UUID PRIMARY KEY
specialist_id   UUID FK → specialist_profiles(id)
domain          VARCHAR  -- 'AI/ML', 'Law', 'Finance', 'Medicine', 'Engineering',
                         -- 'Design', 'Marketing', 'Education', 'Science', 'Business', 'Other'
```

### specialist_languages
```sql
id              UUID PRIMARY KEY
specialist_id   UUID FK → specialist_profiles(id)
language        VARCHAR
proficiency     ENUM('basic', 'conversational', 'fluent', 'native')
```

### specialist_competencies
```sql
id              UUID PRIMARY KEY
specialist_id   UUID FK → specialist_profiles(id)
label           VARCHAR
url             VARCHAR
display_order   INTEGER DEFAULT 0
```

### reviews
```sql
id              UUID PRIMARY KEY
specialist_id   UUID FK → specialist_profiles(id)
client_id       UUID FK → users(id)
rating          INTEGER CHECK (1-5)
comment         TEXT
created_at      TIMESTAMP DEFAULT now()
UNIQUE(specialist_id, client_id)
```

### chat_rooms
```sql
id              UUID PRIMARY KEY
client_id       UUID FK → users(id)
specialist_id   UUID FK → users(id)
created_at      TIMESTAMP DEFAULT now()
UNIQUE(client_id, specialist_id)
```

### messages
```sql
id          UUID PRIMARY KEY
room_id     UUID FK → chat_rooms(id)
sender_id   UUID FK → users(id)
content     TEXT NOT NULL
is_read     BOOLEAN DEFAULT false
created_at  TIMESTAMP DEFAULT now()
```

### task_requests
```sql
id          UUID PRIMARY KEY
client_id   UUID FK → users(id)
domain      TEXT NOT NULL
urgency     ENUM('low', 'medium', 'high', 'urgent')
comment     TEXT
budget_min  DECIMAL(10,2)
budget_max  DECIMAL(10,2)
status      ENUM('open', 'in_progress', 'closed') DEFAULT 'open'
created_at  TIMESTAMP(tz)
updated_at  TIMESTAMP(tz)
```

### task_proposals
```sql
id              UUID PRIMARY KEY
request_id      UUID FK → task_requests(id)
specialist_id   UUID FK → users(id)
message         TEXT
price_offer     DECIMAL(10,2)
created_at      TIMESTAMP(tz)
UNIQUE(request_id, specialist_id)
```

### lesson_plans
```sql
id              UUID PRIMARY KEY
room_id         UUID FK → chat_rooms(id)
specialist_id   UUID FK → users(id)
status          ENUM('generating', 'completed', 'failed')
lesson_content  TEXT
practice_exercises TEXT
homework        TEXT
language        VARCHAR(10)
error_message   TEXT
created_at      TIMESTAMP(tz)
```

---

## 🔍 Smart Search & Matching System

### How it works

The search/matching system uses **multi-criteria scoring** instead of exact domain string matching.

#### Domain Affinity Map (`app/utils/domain_affinity.py`)
Static dictionary mapping related domains with affinity weights (0-1):
- AI/ML ↔ Engineering (0.7), Science (0.6), Education (0.3)
- Law ↔ Business (0.6), Finance (0.5)
- Finance ↔ Business (0.7), Law (0.5), Marketing (0.3)
- etc.

When filtering by domain, **related domains are included** — selecting "AI/ML" also shows Engineering, Science, Education specialists.

#### Scoring Formula (`app/utils/scoring.py`)
```
score = 0.35 * domain_score + 0.25 * text_score + 0.20 * budget_score + 0.15 * rating_score + 0.05 * availability
```

| Factor | Weight | Logic |
|--------|--------|-------|
| domain_score | 0.35 | exact=1.0, related=affinity value, none=0 |
| text_score | 0.25 | keyword overlap (task comment vs specialist bio/headline) |
| budget_score | 0.20 | 1.0 in range, linear decay outside |
| rating_score | 0.15 | avg_rating / 5.0 |
| availability | 0.05 | available=1.0, else=0 |

#### "Other" Domain Logic
When domain="Other", domain_score is neutral (0.5 for all). The primary ranking factor becomes **text matching**: the task's `comment` is compared against specialist `bio`/`headline` via keyword overlap. Budget + rating further differentiate.

#### General Search (GET /specialists/)
- Text search: ILIKE on headline, bio, full_name
- Domain filter: expanded to include related domains via affinity map
- Sort options: rating (default), relevance, price_asc, price_desc
- "relevance" sort: available-first + rating

#### Task Matching (GET /requests/{id}/specialists)
- Fetches broad candidate set (related domains, no strict budget filter)
- Scores each candidate with the formula above
- For "Other" domain: ILIKE pre-filter on comment words, then text-rank scoring
- Returns `relevance_score` (0-100%) on each specialist
- Frontend shows "92% match" badge on SpecialistCard

---

## 🤖 AI Lesson Plans

### How it works
- Specialist clicks "✨ Lesson Plan" in chat room
- Backend reads last 50 messages from the chat
- Sends to Claude API (claude-sonnet-4-20250514) with structured prompt
- Returns: lesson_content (1500-2500 words), practice_exercises (5-7), homework (3-4)
- Frontend shows 3-tab panel (Lesson / Practice / Homework) with Markdown rendering

### Key files
- `app/services/lesson_plan_service.py` — Claude API call, max_tokens=8192, timeout=120s
- `app/routers/lesson_plans.py` — POST /lesson-plans/generate, GET /lesson-plans/room/{room_id}
- `src/components/LessonPlanPanel/index.jsx` — 3-tab UI, copy buttons, regenerate
- `src/api/lessonPlans.js` — API calls

### Known issues & fixes applied
- Claude API sometimes returns markdown code fences around JSON → stripping logic added
- Variable `ai_response` must be initialized before try block for proper error handling
- API key existence check added before making the call

---

## 👤 User Roles & Permissions

| Action | Client | Specialist | Public |
|---|---|---|---|
| Search specialists | ✅ | ✅ | ✅ |
| View specialist profile | ✅ | ✅ | ✅ |
| Start a chat | ✅ | ❌ | ❌ |
| Reply in chat | ✅ | ✅ | ❌ |
| Leave a review | ✅ | ❌ | ❌ |
| Create task request | ✅ | ❌ | ❌ |
| Submit proposal | ❌ | ✅ | ❌ |
| Generate lesson plan | ❌ | ✅ | ❌ |
| Create/edit profile card | ❌ | ✅ | ❌ |
| Upload avatar | ❌ | ✅ | ❌ |
| Add competency proofs | ❌ | ✅ | ❌ |
| Toggle availability | ❌ | ✅ | ❌ |

---

## 🔐 Auth Flow

1. Register → choose role (client or specialist) → POST /auth/register → returns access + refresh tokens
2. Login → POST /auth/login → returns access + refresh tokens
3. Tokens stored in localStorage
4. Access token expires in 30 min → use refresh token to get new one
5. Every protected route: `Authorization: Bearer <access_token>` header
6. Backend dependency `get_current_user` decodes JWT → returns user object
7. Role check done in dependencies: `require_client`, `require_specialist`

---

## 💬 WebSocket Chat

- Server: `python-socketio` mounted on FastAPI via ASGIApp wrapper
- **Important:** The ASGI app is `app.main:application` (not `app.main:app`) — `application` is the socketio ASGI wrapper
- Client: `socket.io-client`
- Auth: JWT token passed as query param on connect `?token=<access_token>`
- Events:
  ```
  join_room(room_id)         — client joins a chat room
  send_message(room_id, text) — send a message
  message_received(msg)      — broadcast to room members
  mark_read(room_id)         — mark messages as read
  user_online(user_id)       — presence indicator
  user_offline(user_id)      — presence indicator
  ```
- Message history loaded via REST GET /chats/{room_id}/messages on room open
- Avatars displayed in chat list and chat room header

---

## 🚀 Development Commands

### Backend
```bash
cd bridge-backend

# Install deps
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server (NOTE: use 'application' not 'app' for socketio support)
uvicorn app.main:application --reload --port 8000

# Seed demo data
python scripts/seed.py

# Run tests
pytest -xvs

# Lint
ruff check . && ruff format .
```

### Frontend
```bash
cd bridge-frontend

# Install deps
npm install

# Start dev server
npm run dev         # runs on localhost:5173

# Build
npm run build

# Lint
npm run lint
```

---

## 🌍 Demo Deployment

### Backend → Railway.app
- Dockerfile ready: `bridge-backend/Dockerfile` (python:3.11-slim)
- Railway config: `bridge-backend/railway.json` (DOCKERFILE builder, healthcheck /health)
- Startup: `alembic upgrade head && uvicorn app.main:application --host 0.0.0.0 --port $PORT`
- Env vars needed: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `ANTHROPIC_API_KEY`
- ⚠️ Railway's `DATABASE_URL` uses `postgres://` — may need replacing with `postgresql+asyncpg://`

### Frontend → Vercel
- Config: `bridge-frontend/vercel.json` (framework: vite, SPA rewrites)
- Env vars: `VITE_API_URL` = Railway backend URL, `VITE_WS_URL` = Railway backend URL
- Auto-deploys on push to main

### Demo accounts (after seed.py)
```
Client:     client@demo.com   / Demo1234!
Specialist: expert@demo.com   / Demo1234!
```

---

## ⚠️ Critical Rules — Never Break These

1. **English only** in UI — no hardcoded non-English strings anywhere
2. **Async only** in backend — no sync DB calls, ever
3. **No payments** — Bridge does not process money, only connects people
4. **No verification** — competency proofs are on trust, no validation logic
5. **One review per client/specialist pair** — enforced at DB level with UNIQUE constraint
6. **Tailwind only** — no custom CSS files, no inline styles
7. **Type hints on all Python functions** — no exceptions
8. **Pydantic v2 syntax** — use `model_config = ConfigDict(...)`, not `class Config`
9. **Write migrations for every model change** — never edit DB directly
10. **Seed script must work standalone** — `python scripts/seed.py` with no extra setup
11. **Use `app.main:application`** for uvicorn — not `app.main:app` (socketio ASGI wrapper)

---

## 🧪 Seed Data (scripts/seed.py)

Current seed creates:
- **25 specialists** with varied domains (including "Other"), languages, rates ($20-$300/hr), availability (available/busy/vacation), ratings (3.0-5.0), competency proofs
- **10 clients**
- **5 chat rooms** with 5-10 messages each
- **15 reviews** (ratings 2-5, not just high ones)
- **10 task requests** (different domains + "Other")
- **8 proposals**

Demo credentials:
```
client@demo.com    / Demo1234!   → role: client
expert@demo.com    / Demo1234!   → role: specialist (featured profile)
```

---

## 📝 Session Log — What Was Done

### Features Implemented
1. **AI Lesson Plan Generator** — Claude API integration, 3-tab UI, mocked in tests
2. **Specialist Avatars** — upload endpoint, display in search cards, chat list, chat room header
3. **Task Request System** — 4-step wizard, proposals, status management
4. **Smart Search & Matching** — domain affinity map, multi-criteria scoring, "Other" domain text matching, relevance badges
5. **"Other" Domain** — added to all frontend domain lists + smart backend handling
6. **Deployment Configs** — Dockerfile, railway.json, vercel.json, alembic.ini fixed
7. **Expanded Seed Data** — 25 specialists, 10 clients, 15 reviews, 10 task requests
8. **Test Suite** — auth, specialists, chats, lesson plans, load tests

### Key Decisions
- **No FTS tsvector column yet** — using ILIKE + Python-side scoring for now. Works on both PostgreSQL and SQLite (tests). Can add tsvector as optimization later (Шаг 3 in plan).
- **Scoring in Python, not SQL** — candidates are fetched broadly from DB, then scored and sorted in Python. Fine for <100 candidates (MVP scale).
- **Domain affinity is static** — hardcoded in `domain_affinity.py`. No DB table needed.
- **relevance_score is a dynamic attribute** — set on ORM objects in Python before serialization, not a DB column.

### Known Issues
- **Test teardown error** — `asyncpg.InterfaceError: cannot perform operation: another operation is in progress` during `conftest.py` teardown. This is a test infrastructure issue (async session cleanup), not related to application code. Tests themselves pass but teardown fails.
- **Alembic migration for lesson_plans** — needs to be run when DB is available (`alembic upgrade head`)
- **Port 8000 conflicts** — if uvicorn fails with "address already in use", kill the previous process first

### What's Left to Do
- [ ] Fix test teardown issue in `conftest.py`
- [ ] Add PostgreSQL tsvector + GIN index for FTS (performance optimization, optional for demo)
- [ ] Deploy to Railway (backend) + Vercel (frontend)
- [ ] Run seed on deployed DB
- [ ] Multi-browser testing (2+ simultaneous users in chat)
- [ ] WebSocket multi-user test (`test_websocket_multiuser.py` — planned but not written)
- [ ] Dashboard "Recent Conversations" avatar display (mentioned, not addressed)
