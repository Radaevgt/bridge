import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.specialist import SpecialistProfileResponse
from app.schemas.task_request import (
    TaskProposalCreate,
    TaskProposalResponse,
    TaskRequestCreate,
    TaskRequestListResponse,
    TaskRequestResponse,
    TaskRequestStatusUpdate,
)
from app.services.task_request_service import TaskRequestService
from app.utils.deps import get_current_user, require_client, require_specialist

router = APIRouter(prefix="/requests", tags=["task_requests"])


@router.post(
    "/",
    response_model=TaskRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_request(
    data: TaskRequestCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
) -> TaskRequestResponse:
    service = TaskRequestService(db)
    request = await service.create_request(current_user.id, data)
    return _build_request_response(request)


@router.get("/", response_model=list[TaskRequestListResponse])
async def list_requests(
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskRequestListResponse]:
    service = TaskRequestService(db)

    if current_user.role == UserRole.CLIENT:
        requests = await service.get_client_requests(current_user.id, page)
    else:
        requests = await service.get_matching_requests_for_specialist(
            current_user.id, page
        )

    return [
        TaskRequestListResponse(
            id=r.id,
            client_id=r.client_id,
            domain=r.domain,
            urgency=r.urgency,
            comment=r.comment,
            budget_min=float(r.budget_min) if r.budget_min else None,
            budget_max=float(r.budget_max) if r.budget_max else None,
            status=r.status,
            created_at=r.created_at,
            updated_at=r.updated_at,
            client={"id": r.client.id, "full_name": r.client.full_name, "avatar_url": r.client.avatar_url}
            if r.client
            else None,
            proposal_count=len(r.proposals),
        )
        for r in requests
    ]


@router.get("/{request_id}", response_model=TaskRequestResponse)
async def get_request_detail(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskRequestResponse:
    service = TaskRequestService(db)
    request = await service.get_request_detail(request_id, current_user.id)
    return _build_request_response(request)


@router.get(
    "/{request_id}/specialists",
    response_model=list[SpecialistProfileResponse],
)
async def get_matching_specialists(
    request_id: uuid.UUID,
    page: int = Query(1, ge=1),
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
) -> list[SpecialistProfileResponse]:
    service = TaskRequestService(db)
    return await service.get_matching_specialists(
        request_id, current_user.id, page
    )


@router.post(
    "/{request_id}/proposals",
    response_model=TaskProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_proposal(
    request_id: uuid.UUID,
    data: TaskProposalCreate,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> TaskProposalResponse:
    service = TaskRequestService(db)
    proposal = await service.create_proposal(request_id, current_user.id, data)
    return TaskProposalResponse(
        id=proposal.id,
        request_id=proposal.request_id,
        specialist_id=proposal.specialist_id,
        message=proposal.message,
        price_offer=float(proposal.price_offer) if proposal.price_offer else None,
        created_at=proposal.created_at,
        specialist={"id": proposal.specialist.id, "full_name": proposal.specialist.full_name, "avatar_url": proposal.specialist.avatar_url}
        if proposal.specialist
        else None,
    )


@router.patch("/{request_id}/status", response_model=TaskRequestResponse)
async def update_request_status(
    request_id: uuid.UUID,
    data: TaskRequestStatusUpdate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
) -> TaskRequestResponse:
    service = TaskRequestService(db)
    request = await service.update_request_status(
        request_id, current_user.id, data
    )
    return _build_request_response(request)


def _build_request_response(request: object) -> TaskRequestResponse:
    """Build a full TaskRequestResponse from a TaskRequest ORM object."""
    return TaskRequestResponse(
        id=request.id,
        client_id=request.client_id,
        domain=request.domain,
        urgency=request.urgency,
        comment=request.comment,
        budget_min=float(request.budget_min) if request.budget_min else None,
        budget_max=float(request.budget_max) if request.budget_max else None,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
        client={"id": request.client.id, "full_name": request.client.full_name, "avatar_url": request.client.avatar_url}
        if request.client
        else None,
        proposals=[
            TaskProposalResponse(
                id=p.id,
                request_id=p.request_id,
                specialist_id=p.specialist_id,
                message=p.message,
                price_offer=float(p.price_offer) if p.price_offer else None,
                created_at=p.created_at,
                specialist={"id": p.specialist.id, "full_name": p.specialist.full_name, "avatar_url": p.specialist.avatar_url}
                if p.specialist
                else None,
            )
            for p in request.proposals
        ],
        proposal_count=len(request.proposals),
    )
