# Pydantic v2 Schemas Skill

> Trigger: creating request/response models, validation, serialization

## Schema Templates

### Response Schema (from ORM)
```python
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    created_at: datetime
```

### Request Schema (validation)
```python
from pydantic import BaseModel, Field, EmailStr

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    rating: int = Field(ge=1, le=5)
    tags: list[str] = []
```

### Nested Schemas
```python
class DomainSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    domain: str

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    domains: list[DomainSchema] = []
```

## Rules — CRITICAL
- **Pydantic v2 ONLY** — use `model_config = ConfigDict(...)`, NEVER `class Config:`
- `from_attributes=True` for ORM → Pydantic conversion
- `Field(ge=1, le=5)` for numeric constraints
- `str | None = None` for optional fields (Python 3.11 union syntax)
- `EmailStr` for email validation (requires `pydantic[email]`)
- Always validate inputs — never trust client data
- Response models strip sensitive fields (no password_hash in responses)
