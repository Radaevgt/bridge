import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.specialist import (
    Availability,
    SpecialistCompetency,
    SpecialistDomain,
    SpecialistLanguage,
    SpecialistProfile,
)
from app.models.user import User
from app.schemas.specialist import CompetencyCreate, SpecialistProfileCreate
from app.utils.domain_affinity import get_all_related_domain_names

PAGE_SIZE = 12


def _profile_load_options() -> list:
    """Shared eager-load options for SpecialistProfile queries."""
    return [
        selectinload(SpecialistProfile.user),
        selectinload(SpecialistProfile.domains),
        selectinload(SpecialistProfile.languages),
        selectinload(SpecialistProfile.competencies),
    ]


class SpecialistService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(
        self,
        search: str | None = None,
        domain: list[str] | None = None,
        language: list[str] | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        availability_only: bool = False,
        sort: str = "rating",
        page: int = 1,
    ) -> list[SpecialistProfile]:
        query = (
            select(SpecialistProfile)
            .join(User, SpecialistProfile.user_id == User.id)
            .options(*_profile_load_options())
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    SpecialistProfile.headline.ilike(pattern),
                    SpecialistProfile.bio.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )

        if domain:
            # Expand domain filter to include related domains via affinity map
            expanded_domains: set[str] = set()
            for d in domain:
                related = get_all_related_domain_names(d)
                expanded_domains.update(related if related else [d])
            query = query.join(SpecialistDomain).where(
                SpecialistDomain.domain.in_(list(expanded_domains))
            )

        if language:
            query = query.join(SpecialistLanguage).where(
                SpecialistLanguage.language.in_(language)
            )

        if min_price is not None:
            query = query.where(SpecialistProfile.hourly_rate >= min_price)
        if max_price is not None:
            query = query.where(SpecialistProfile.hourly_rate <= max_price)
        if min_rating is not None:
            query = query.where(SpecialistProfile.avg_rating >= min_rating)
        if availability_only:
            query = query.where(
                SpecialistProfile.availability == Availability.AVAILABLE
            )

        if sort == "price_asc":
            query = query.order_by(SpecialistProfile.hourly_rate.asc())
        elif sort == "price_desc":
            query = query.order_by(SpecialistProfile.hourly_rate.desc())
        elif sort == "relevance":
            # For general search, relevance = rating + availability preference
            query = query.order_by(
                SpecialistProfile.availability.asc(),  # 'available' first
                SpecialistProfile.avg_rating.desc(),
            )
        else:
            query = query.order_by(SpecialistProfile.avg_rating.desc())

        query = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def get_by_id(self, specialist_id: uuid.UUID) -> SpecialistProfile | None:
        result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.id == specialist_id)
            .options(*_profile_load_options())
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> SpecialistProfile | None:
        result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.user_id == user_id)
            .options(*_profile_load_options())
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, user_id: uuid.UUID, data: SpecialistProfileCreate
    ) -> SpecialistProfile:
        result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.user_id == user_id)
            .options(*_profile_load_options())
        )
        profile = result.scalar_one_or_none()

        if profile is None:
            profile = SpecialistProfile(user_id=user_id)
            self.db.add(profile)

        profile.headline = data.headline
        profile.bio = data.bio
        profile.hourly_rate = data.hourly_rate

        # Replace domains
        profile.domains.clear()
        for d in data.domains:
            profile.domains.append(SpecialistDomain(domain=d))

        # Replace languages — now uses typed LanguageCreateSchema
        profile.languages.clear()
        for lang in data.languages:
            profile.languages.append(
                SpecialistLanguage(language=lang.language, proficiency=lang.proficiency)
            )

        await self.db.commit()

        # Re-fetch with all relationships eagerly loaded
        result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.id == profile.id)
            .options(*_profile_load_options())
        )
        return result.scalar_one()

    async def add_competency(
        self, user_id: uuid.UUID, data: CompetencyCreate
    ) -> SpecialistCompetency:
        profile = await self._get_profile_by_user(user_id)
        comp = SpecialistCompetency(
            specialist_id=profile.id,
            label=data.label,
            url=data.url,
            display_order=data.display_order,
        )
        self.db.add(comp)
        await self.db.commit()
        await self.db.refresh(comp)
        return comp

    async def delete_competency(
        self, user_id: uuid.UUID, competency_id: uuid.UUID
    ) -> None:
        profile = await self._get_profile_by_user(user_id)
        result = await self.db.execute(
            select(SpecialistCompetency).where(
                SpecialistCompetency.id == competency_id,
                SpecialistCompetency.specialist_id == profile.id,
            )
        )
        comp = result.scalar_one_or_none()
        if not comp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Competency not found"
            )
        await self.db.delete(comp)
        await self.db.commit()

    async def update_availability(
        self, user_id: uuid.UUID, availability: Availability
    ) -> SpecialistProfile:
        profile = await self._get_profile_by_user(user_id)
        profile.availability = availability
        await self.db.commit()

        # Re-fetch with all relationships eagerly loaded
        result = await self.db.execute(
            select(SpecialistProfile)
            .where(SpecialistProfile.id == profile.id)
            .options(*_profile_load_options())
        )
        return result.scalar_one()

    async def _get_profile_by_user(self, user_id: uuid.UUID) -> SpecialistProfile:
        result = await self.db.execute(
            select(SpecialistProfile).where(SpecialistProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialist profile not found",
            )
        return profile
