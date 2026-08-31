import uuid
from typing import Optional, List
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, joinedload, selectinload
from backend.app.models.assessment import Assessment
from backend.app.models.assessment_question import AssessmentQuestion
from backend.app.models.assessment_result import AssessmentResult


class AssessmentRepository:
    """Repository handling database operations for Assessments, Questions, and Results."""

    @staticmethod
    def get_all(
        db: Session,
        skill_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Assessment]:
        """Fetch available assessments in the catalog with skill and question count."""
        stmt = (
            select(Assessment)
            .options(
                joinedload(Assessment.skill),
                selectinload(Assessment.questions)
            )
        )
        if skill_id:
            stmt = stmt.where(Assessment.skill_id == skill_id)

        stmt = stmt.order_by(Assessment.title).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, assessment_id: uuid.UUID) -> Optional[Assessment]:
        """Fetch assessment by ID with skill and questions."""
        return db.execute(
            select(Assessment)
            .options(
                joinedload(Assessment.skill),
                selectinload(Assessment.questions)
            )
            .where(Assessment.id == assessment_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_max_attempt_number(db: Session, assessment_id: uuid.UUID, learner_id: uuid.UUID) -> int:
        """Find highest attempt number for a learner on a given assessment."""
        result = db.execute(
            select(func.max(AssessmentResult.attempt_number))
            .where(
                AssessmentResult.assessment_id == assessment_id,
                AssessmentResult.learner_id == learner_id
            )
        ).scalar()
        return result or 0

    @staticmethod
    def create_result(
        db: Session,
        assessment_id: uuid.UUID,
        learner_id: uuid.UUID,
        score: float,
        skill_mastery: float,
        attempt_number: int
    ) -> AssessmentResult:
        """Persist a new assessment attempt result."""
        res = AssessmentResult(
            assessment_id=assessment_id,
            learner_id=learner_id,
            score=score,
            skill_mastery=skill_mastery,
            attempt_number=attempt_number
        )
        db.add(res)
        db.flush()
        return res

    @staticmethod
    def get_learner_results(
        db: Session,
        learner_id: uuid.UUID,
        assessment_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[AssessmentResult]:
        """Retrieve learner assessment history with assessment and skill relations."""
        stmt = (
            select(AssessmentResult)
            .options(
                joinedload(AssessmentResult.assessment).joinedload(Assessment.skill)
            )
            .where(AssessmentResult.learner_id == learner_id)
        )
        if assessment_id:
            stmt = stmt.where(AssessmentResult.assessment_id == assessment_id)

        stmt = stmt.order_by(desc(AssessmentResult.created_at)).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_result_by_id(db: Session, result_id: uuid.UUID) -> Optional[AssessmentResult]:
        """Fetch single assessment result by ID."""
        return db.execute(
            select(AssessmentResult)
            .options(
                joinedload(AssessmentResult.assessment).joinedload(Assessment.skill)
            )
            .where(AssessmentResult.id == result_id)
        ).scalar_one_or_none()
