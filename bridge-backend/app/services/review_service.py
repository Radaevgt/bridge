import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.specialist import SpecialistProfile
from app.schemas.review import ReviewCreate


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_review(
        self, specialist_id: uuid.UUID, client_id: uuid.UUID, data: ReviewCreate
    ) -> Review:
        # Check specialist exists
        result = await self.db.execute(
            select(SpecialistProfile).where(SpecialistProfile.id == specialist_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found"
            )

        # Check duplicate
        result = await self.db.execute(
            select(Review).where(
                Review.specialist_id == specialist_id, Review.client_id == client_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already reviewed this specialist",
            )

        # Save review FIRST so it's visible to the aggregate query
        review = Review(
            specialist_id=specialist_id,
            client_id=client_id,
            rating=data.rating,
            comment=data.comment,
        )
        self.db.add(review)
        await self.db.flush()  # flush to DB so AVG/COUNT see the new row

        # Recalculate avg rating from ALL reviews (including the one just flushed)
        result = await self.db.execute(
            select(func.avg(Review.rating), func.count(Review.id)).where(
                Review.specialist_id == specialist_id
            )
        )
        row = result.one()
        profile.avg_rating = round(float(row[0] or 0), 2)
        profile.review_count = int(row[1] or 0)

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_reviews(self, specialist_id: uuid.UUID) -> list[Review]:
        result = await self.db.execute(
            select(Review)
            .where(Review.specialist_id == specialist_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())
