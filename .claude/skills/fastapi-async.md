# FastAPI Async Patterns Skill

> Trigger: creating endpoints, adding routes, middleware, dependencies, error handling

## Endpoint Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.deps import get_current_user, require_client, require_specialist

router = APIRouter(prefix="/resource", tags=["resource"])


@router.get("/", response_model=list[ResponseSchema])
async def list_items(
    db: AsyncSession = Depends(get_db),
) -> list[ResponseSchema]:
    service = MyService(db)
    return await service.list_all()


@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: CreateSchema,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema:
    service = MyService(db)
    return await service.create(current_user.id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = MyService(db)
    await service.delete(item_id, current_user.id)
```

## Service Layer Template

```python
class MyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[Model]:
        result = await self.db.execute(select(Model).order_by(Model.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, item_id: uuid.UUID) -> Model | None:
        result = await self.db.execute(select(Model).where(Model.id == item_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, data: CreateSchema) -> Model:
        item = Model(**data.model_dump(), user_id=user_id)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
```

## Rules
- **ALWAYS async** — `async def` on every endpoint and service method
- **Type hints on every function** — no exceptions
- **Depends()** for DB session, auth, role checks
- **HTTP status codes**: 201 create, 204 delete, 404 not found, 409 conflict, 422 validation
- **Never sync DB calls** — no `session.query()`, only `await db.execute(select(...))`
- Router → Service → DB (never direct DB access in routers)
- All error messages in English
