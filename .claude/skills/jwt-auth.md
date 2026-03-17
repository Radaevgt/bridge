# JWT Authentication Skill

> Trigger: auth, login, register, tokens, protected routes, role-based access

## Auth Flow

```
Register/Login
  → Backend generates: access_token (30min) + refresh_token (7 days)
  → Client stores in localStorage
  → Every request: Authorization: Bearer <access_token>
  → On 401: auto-refresh via interceptor
  → On refresh fail: redirect to /login
```

## Backend Token Generation
```python
from datetime import datetime, timedelta, timezone
from jose import jwt

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({**data, "exp": expire, "type": "access"}, SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({**data, "exp": expire, "type": "refresh"}, SECRET_KEY, algorithm="HS256")
```

## Backend Dependencies
```python
# Get any authenticated user
async def get_current_user(credentials, db) -> User:
    token = credentials.credentials
    payload = decode_token(token)  # validates exp + type
    user = await db.get(User, uuid.UUID(payload["sub"]))
    return user

# Require specific role
async def require_client(user = Depends(get_current_user)) -> User:
    if user.role != UserRole.CLIENT:
        raise HTTPException(403, "Client role required")
    return user

async def require_specialist(user = Depends(get_current_user)) -> User:
    if user.role != UserRole.SPECIALIST:
        raise HTTPException(403, "Specialist role required")
    return user
```

## Frontend Axios Interceptors
```javascript
// Request: attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response: auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const { data } = await axios.post('/auth/refresh', {
        refresh_token: localStorage.getItem('refresh_token')
      });
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return api(error.config);  // retry original request
    }
    return Promise.reject(error);
  }
);
```

## Password Rules
- **NEVER store plain passwords** — always bcrypt
- `passlib.context.CryptContext(schemes=["bcrypt"])`
- `hash_password(plain)` → store in DB
- `verify_password(plain, hashed)` → check on login

## Permissions Matrix
| Action               | Public | Client | Specialist |
|----------------------|--------|--------|------------|
| Search specialists   | ✅     | ✅     | ✅         |
| View profiles        | ✅     | ✅     | ✅         |
| Start a chat         | ❌     | ✅     | ❌         |
| Reply in chat        | ❌     | ✅     | ✅         |
| Leave a review       | ❌     | ✅     | ❌         |
| Edit own profile     | ❌     | ❌     | ✅         |
| Add competency       | ❌     | ❌     | ✅         |
| Toggle availability  | ❌     | ❌     | ✅         |
