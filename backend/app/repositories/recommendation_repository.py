import uuid
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session, joinedload
from backend.app.models.recommendation import Recommendation
from backend.app.models.feedback import Feedback


class RecommendationRepository:
    """Repository handling database operations for recommendations and learner feedback."""

    @staticmethod
    def get_by_learner(
        db: Session,
        learner_id: uuid.UUID,
        limit: int = 20
    ) -> List[Recommendation]:
        """Fetch latest recommendations for a learner with resource and skill relations."""
        return db.execute(
            select(Recommendation)
            .options(
                joinedload(Recommendation.resource),
                joinedload(Recommendation.skill)
            )
            .where(Recommendation.learner_id == learner_id)
            .order_by(Recommendation.ranking.asc(), desc(Recommendation.score))
            .limit(limit)
        ).scalars().all()

    @staticmethod
    def get_by_id(db: Session, recommendation_id: uuid.UUID) -> Optional[Recommendation]:
        """Fetch recommendation by ID with resource and skill relations."""
        return db.execute(
            select(Recommendation)
            .options(
                joinedload(Recommendation.resource),
                joinedload(Recommendation.skill)
            )
            .where(Recommendation.id == recommendation_id)
        ).scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        learner_id: uuid.UUID,
        skill_id: Optional[uuid.UUID],
        resource_id: Optional[uuid.UUID],
        score: float,
        ranking: int,
        reason: dict,
        algorithm_version: str = "v1"
    ) -> Recommendation:
        """Persist a generated recommendation entry."""
        rec = Recommendation(
            learner_id=learner_id,
            skill_id=skill_id,
            resource_id=resource_id,
            score=score,
            ranking=ranking,
            reason=reason,
            algorithm_version=algorithm_version
        )
        db.add(rec)
        db.flush()
        return rec

    @staticmethod
    def clear_previous_recommendations(db: Session, learner_id: uuid.UUID) -> None:
        """Clear previous generated recommendations for clean refreshes."""
        db.query(Recommendation).filter(Recommendation.learner_id == learner_id).delete()
        db.flush()

    @staticmethod
    def create_feedback(
        db: Session,
        learner_id: uuid.UUID,
        resource_id: Optional[uuid.UUID],
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> Feedback:
        """Record learner feedback on a recommended resource."""
        fb = Feedback(
            learner_id=learner_id,
            resource_id=resource_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment
        )
        db.add(fb)
        db.flush()
        return fb

    @staticmethod
    def get_feedback_for_learner(db: Session, learner_id: uuid.UUID) -> List[Feedback]:
        """Retrieve all feedback submitted by learner."""
        return db.execute(
            select(Feedback).where(Feedback.learner_id == learner_id)
        ).scalars().all()
