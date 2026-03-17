import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.specialist import SpecialistDomain, SpecialistProfile
from app.models.task_request import RequestStatus, TaskProposal, TaskRequest
from app.models.user import User
from app.schemas.task_request import TaskProposalCreate, TaskRequestCreate, TaskRequestStatusUpdate
from app.utils.domain_affinity import get_all_related_domain_names, get_related_domains
from app.utils.scoring import score_specialist

PAGE_SIZE = 12

# Maximum candidates to fetch before scoring (prevents unbounded queries)
MAX_CANDIDATES = 100


def _compute_text_rank(
    specialist: SpecialistProfile, search_text: str
) -> float:
    """Simple text-matching score using keyword overlap.

    Compares words from search_text against specialist's headline and bio.
    Returns a score between 0 and 1.
    """
    if not search_text:
        return 0.0

    search_words = set(search_text.lower().split())
    if not search_words:
        return 0.0

    # Build a bag of words from specialist's profile
    profile_text = ""
    if specialist.headline:
        profile_text += specialist.headline.lower() + " "
    if specialist.bio:
        profile_text += specialist.bio.lower()

    if not profile_text:
        return 0.0

    profile_words = set(profile_text.split())

    # Jaccard-like overlap: matched words / total search words
    matched = search_words & profile_words
    return len(matched) / len(search_words) if search_words else 0.0


class TaskRequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_request(
        self, client_id: uuid.UUID, data: TaskRequestCreate
    ) -> TaskRequest:
        request = TaskRequest(
            client_id=client_id,
            domain=data.domain,
            urgency=data.urgency,
            comment=data.comment,
            budget_min=data.budget_min,
            budget_max=data.budget_max,
        )
        self.db.add(request)
        await self.db.commit()

        return await self._get_request_by_id(request.id)

    async def get_client_requests(
        self, client_id: uuid.UUID, page: int = 1
    ) -> list[TaskRequest]:
        """Get all requests created by a specific client."""
        query = (
            select(TaskRequest)
            .where(TaskRequest.client_id == client_id)
            .options(
                selectinload(TaskRequest.client),
                selectinload(TaskRequest.proposals).selectinload(
                    TaskProposal.specialist
                ),
            )
            .order_by(TaskRequest.created_at.desc())
            .offset((page - 1) * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def get_matching_requests_for_specialist(
        self, specialist_user_id: uuid.UUID, page: int = 1
    ) -> list[TaskRequest]:
        """Get open requests matching a specialist's domains (with affinity)."""
        profile_result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.user_id == specialist_user_id)
            .options(selectinload(SpecialistProfile.domains))
        )
        profile = profile_result.scalar_one_or_none()

        if not profile or not profile.domains:
            return []

        domain_names = [d.domain for d in profile.domains]

        # If specialist has "Other" domain → show all open requests
        has_other = "Other" in domain_names

        query = select(TaskRequest).where(TaskRequest.status == RequestStatus.OPEN)

        if not has_other:
            # Expand to related domains so specialist sees relevant requests
            expanded_domains: set[str] = set()
            for d in domain_names:
                related = get_all_related_domain_names(d)
                expanded_domains.update(related if related else [d])
            # Also include "Other" domain requests — they're open to everyone
            query = query.where(
                or_(
                    TaskRequest.domain.in_(list(expanded_domains)),
                    TaskRequest.domain == "Other",
                )
            )

        query = (
            query
            .options(
                selectinload(TaskRequest.client),
                selectinload(TaskRequest.proposals).selectinload(
                    TaskProposal.specialist
                ),
            )
            .order_by(TaskRequest.created_at.desc())
            .offset((page - 1) * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def get_request_detail(
        self, request_id: uuid.UUID, user_id: uuid.UUID
    ) -> TaskRequest:
        """Get a single request with full details."""
        request = await self._get_request_by_id(request_id)

        # Authorization: client owns the request OR any authenticated specialist
        if request.client_id != user_id:
            profile_result = await self.db.execute(
                select(SpecialistProfile).where(
                    SpecialistProfile.user_id == user_id
                )
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )

        return request

    async def create_proposal(
        self,
        request_id: uuid.UUID,
        specialist_user_id: uuid.UUID,
        data: TaskProposalCreate,
    ) -> TaskProposal:
        """A specialist submits a proposal for a task request."""
        request = await self._get_request_by_id(request_id)

        if request.status != RequestStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request is no longer accepting proposals",
            )

        # Check for duplicate proposal
        existing = await self.db.execute(
            select(TaskProposal).where(
                TaskProposal.request_id == request_id,
                TaskProposal.specialist_id == specialist_user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already submitted a proposal for this request",
            )

        proposal = TaskProposal(
            request_id=request_id,
            specialist_id=specialist_user_id,
            message=data.message,
            price_offer=data.price_offer,
        )
        self.db.add(proposal)
        await self.db.commit()

        # Re-fetch with specialist relationship
        result = await self.db.execute(
            select(TaskProposal)
            .where(TaskProposal.id == proposal.id)
            .options(selectinload(TaskProposal.specialist))
        )
        return result.scalar_one()

    async def update_request_status(
        self,
        request_id: uuid.UUID,
        client_id: uuid.UUID,
        data: TaskRequestStatusUpdate,
    ) -> TaskRequest:
        """Client updates the status of their own request."""
        request = await self._get_request_by_id(request_id)

        if request.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the request owner can update its status",
            )

        request.status = data.status
        await self.db.commit()

        return await self._get_request_by_id(request_id)

    async def get_matching_specialists(
        self,
        request_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
    ) -> list[dict]:
        """Return specialists matching a task request, ranked by relevance score.

        Uses multi-criteria scoring: domain affinity + text match + budget fit
        + rating + availability.
        """
        request = await self._get_request_by_id(request_id)

        if request.client_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the request owner can view matching specialists",
            )

        # Step 1: Fetch a broad candidate set
        query = (
            select(SpecialistProfile)
            .join(User, SpecialistProfile.user_id == User.id)
            .options(
                selectinload(SpecialistProfile.user),
                selectinload(SpecialistProfile.domains),
                selectinload(SpecialistProfile.languages),
                selectinload(SpecialistProfile.competencies),
            )
        )

        # Only filter by availability (hard constraint)
        query = query.where(
            SpecialistProfile.availability == "available"
        )

        # For non-"Other" domains, filter to related domains (broader than before)
        if request.domain != "Other":
            related_names = get_all_related_domain_names(request.domain)
            if related_names:
                query = (
                    query
                    .join(SpecialistDomain, SpecialistDomain.specialist_id == SpecialistProfile.id)
                    .where(SpecialistDomain.domain.in_(related_names))
                )

        # For "Other" domain + text comment: use ILIKE to pre-filter
        if request.domain == "Other" and request.comment:
            # Extract key words for a broad ILIKE filter (first 3 significant words)
            words = [w for w in request.comment.split() if len(w) > 3][:3]
            if words:
                conditions = []
                for word in words:
                    pattern = f"%{word}%"
                    conditions.append(SpecialistProfile.headline.ilike(pattern))
                    conditions.append(SpecialistProfile.bio.ilike(pattern))
                query = query.where(or_(*conditions))

        query = query.limit(MAX_CANDIDATES)
        result = await self.db.execute(query)
        candidates = list(result.scalars().unique().all())

        # Step 2: Score each candidate
        search_text = request.comment or ""
        scored: list[tuple[SpecialistProfile, float]] = []

        for specialist in candidates:
            text_rank = _compute_text_rank(specialist, search_text)
            relevance = score_specialist(
                specialist=specialist,
                target_domain=request.domain,
                budget_min=float(request.budget_min) if request.budget_min else None,
                budget_max=float(request.budget_max) if request.budget_max else None,
                text_rank=text_rank,
            )
            scored.append((specialist, relevance))

        # Step 3: Sort by relevance score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Step 4: Paginate
        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_results = scored[start:end]

        # Step 5: Attach relevance_score to each specialist object
        for specialist, score in page_results:
            specialist.relevance_score = round(score * 100, 1)  # as percentage

        return [sp for sp, _ in page_results]

    async def _get_request_by_id(self, request_id: uuid.UUID) -> TaskRequest:
        result = await self.db.execute(
            select(TaskRequest)
            .where(TaskRequest.id == request_id)
            .options(
                selectinload(TaskRequest.client),
                selectinload(TaskRequest.proposals).selectinload(
                    TaskProposal.specialist
                ),
            )
        )
        request = result.scalar_one_or_none()
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task request not found",
            )
        return request
