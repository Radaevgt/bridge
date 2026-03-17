# Alembic Migrations Skill

> Trigger: database changes, new columns, new tables, schema modifications, migrations

## Commands

```bash
# Generate migration from model changes
cd bridge-backend
alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

## Async Alembic Configuration (already set up)

`alembic/env.py` uses `async_engine_from_config` + `asyncio.run()` for async PostgreSQL.

All models must be imported in `app/models/__init__.py` so Alembic sees them:
```python
from app.models.user import Base, User
from app.models.specialist import SpecialistProfile, SpecialistDomain, ...
from app.models.review import Review
from app.models.chat import ChatRoom, Message
```

## Rules
- **EVERY model change requires a migration** — never edit DB directly
- Run `alembic revision --autogenerate -m "..."` after changing any model
- Always review generated migration before applying
- Test both `upgrade()` and `downgrade()`
- Migration names should be descriptive: "add_avatar_url_to_users", "create_reviews_table"
- UUID columns: `sa.Column(sa.dialects.postgresql.UUID(as_uuid=True))`
- Enums: may need manual `sa.Enum(...)` in migration if autogenerate misses it
