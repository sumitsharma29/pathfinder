import uuid
from typing import List, Optional, Dict, Set
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    NotFoundError, AuthorizationError, ConflictError, AppException
)
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.assessment import Assessment
from backend.app.models.assessment_question import AssessmentQuestion
from backend.app.models.assessment_result import AssessmentResult
from backend.app.repositories.assessment_repository import AssessmentRepository
from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.schemas.roadmap import SkillSummary
from backend.app.schemas.assessment import (
    AssessmentSummary, AssessmentDetailResponse,
    AssessmentQuestionPublic, AssessmentSubmissionRequest,
    AssessmentResultResponse, AssessmentHistoryItem
)


class AssessmentService:
    """Service handling assessment catalog, secure question delivery, server-side scoring, and mastery updates."""

    @classmethod
    def list_assessments(
        cls,
        db: Session,
        skill_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[AssessmentSummary]:
        """Fetch available assessments in the catalog."""
        skip = (page - 1) * page_size
        assessments = AssessmentRepository.get_all(db, skill_id=skill_id, skip=skip, limit=page_size)

        results: List[AssessmentSummary] = []
        for a in assessments:
            skill_summary = SkillSummary(
                id=a.skill.id,
                name=a.skill.name,
                slug=a.skill.slug,
                category=a.skill.category
            ) if a.skill else None

            results.append(
                AssessmentSummary(
                    id=a.id,
                    title=a.title,
                    description=a.description,
                    difficulty=a.difficulty,
                    passing_score=float(a.passing_score),
                    skill=skill_summary,
                    question_count=len(a.questions) if a.questions else 0,
                    created_at=a.created_at
                )
            )
        return results

    @classmethod
    def get_assessment_detail(
        cls,
        db: Session,
        assessment_id: uuid.UUID
    ) -> AssessmentDetailResponse:
        """Fetch assessment details and questions EXCLUDING correct answers and explanations."""
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment:
            raise NotFoundError(message="Assessment not found", details={"assessment_id": str(assessment_id)})

        skill_summary = SkillSummary(
            id=assessment.skill.id,
            name=assessment.skill.name,
            slug=assessment.skill.slug,
            category=assessment.skill.category
        ) if assessment.skill else None

        # Sanitize questions: strip correct_answer and explanation
        public_questions = [
            AssessmentQuestionPublic(
                id=q.id,
                question=q.question,
                question_type=q.question_type,
                options=q.options,
                points=float(q.points)
            )
            for q in assessment.questions
        ]

        return AssessmentDetailResponse(
            id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            difficulty=assessment.difficulty,
            passing_score=float(assessment.passing_score),
            skill=skill_summary,
            questions=public_questions,
            created_at=assessment.created_at
        )

    @classmethod
    def submit_assessment(
        cls,
        db: Session,
        user_id: uuid.UUID,
        assessment_id: uuid.UUID,
        submission: AssessmentSubmissionRequest
    ) -> AssessmentResultResponse:
        """Score submission server-side, calculate mastery, and update learner skills atomically."""
        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).with_for_update().first()
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment:
            raise NotFoundError(message="Assessment not found", details={"assessment_id": str(assessment_id)})

        if not assessment.questions:
            raise AppException(
                status_code=400,
                code="ASSESSMENT_EMPTY",
                message="This assessment has no questions configured."
            )

        # Build map of valid questions in this assessment
        valid_questions: Dict[uuid.UUID, AssessmentQuestion] = {
            q.id: q for q in assessment.questions
        }

        # 1. Validation: Check duplicate submitted question IDs
        submitted_q_ids = [item.question_id for item in submission.answers]
        if len(submitted_q_ids) != len(set(submitted_q_ids)):
            raise AppException(
                status_code=422,
                code="DUPLICATE_QUESTION_SUBMISSION",
                message="Duplicate question answers submitted."
            )

        # 2. Validation: Check for unknown or cross-assessment question IDs
        for q_id in submitted_q_ids:
            if q_id not in valid_questions:
                raise AppException(
                    status_code=422,
                    code="INVALID_QUESTION_ID",
                    message=f"Question {q_id} does not belong to this assessment."
                )

        # 3. Validation: Check that all required questions in this assessment are answered
        missing_q_ids = set(valid_questions.keys()) - set(submitted_q_ids)
        if missing_q_ids:
            raise AppException(
                status_code=422,
                code="INCOMPLETE_SUBMISSION",
                message=f"Submission is missing answers for {len(missing_q_ids)} question(s)."
            )

        # 4. Server-Side Scoring
        total_possible_points = 0.0
        earned_points = 0.0
        correct_count = 0

        submitted_answers_map = {item.question_id: item.answer for item in submission.answers}

        for q_id, question_obj in valid_questions.items():
            q_points = float(question_obj.points)
            total_possible_points += q_points

            user_ans = submitted_answers_map[q_id].strip().upper()
            correct_ans = question_obj.correct_answer.strip().upper()

            if user_ans == correct_ans:
                earned_points += q_points
                correct_count += 1

        score_percentage = (
            round((earned_points / total_possible_points) * 100.0, 2)
            if total_possible_points > 0
            else 0.0
        )
        passed = score_percentage >= float(assessment.passing_score)

        # 5. Attempt Number Determination (Server-controlled)
        max_attempt = AssessmentRepository.get_max_attempt_number(db, assessment.id, profile.id)
        next_attempt_number = max_attempt + 1

        # 6. Skill Mastery Calculation
        # Check existing learner proficiency for this skill
        learner_skills = LearnerProfileRepository.get_learner_skills(db, profile.id)
        current_prof_dict = {ls.skill_id: float(ls.proficiency) for ls in learner_skills}

        if assessment.skill_id in current_prof_dict:
            old_prof = current_prof_dict[assessment.skill_id]
            # Exponential Evidence Fusion: 30% prior + 70% current assessment score
            new_mastery = round(0.30 * old_prof + 0.70 * score_percentage, 2)
        else:
            new_mastery = score_percentage

        new_mastery = max(0.0, min(100.0, new_mastery))

        # 7. Persist Assessment Result
        result_record = AssessmentRepository.create_result(
            db=db,
            assessment_id=assessment.id,
            learner_id=profile.id,
            score=score_percentage,
            skill_mastery=new_mastery,
            attempt_number=next_attempt_number
        )

        # 8. Update Learner Skill State
        if assessment.skill_id:
            LearnerProfileRepository.add_or_update_learner_skill(
                db=db,
                learner_id=profile.id,
                skill_id=assessment.skill_id,
                proficiency=new_mastery,
                source="assessment",
                confidence=0.95
            )

        # 9. Trigger Adaptive Learning Engine (API_SPEC.md §32)
        from backend.app.services.adaptive_learning_service import AdaptiveLearningService
        AdaptiveLearningService.on_assessment_completed(
            db=db,
            user_id=user_id,
            assessment_id=assessment.id,
            score=score_percentage,
            mastery=new_mastery
        )

        db.commit()

        return AssessmentResultResponse(
            id=result_record.id,
            assessment_id=assessment.id,
            assessment_title=assessment.title,
            skill_id=assessment.skill.id if assessment.skill else assessment.skill_id,
            skill_name=assessment.skill.name if assessment.skill else "Unknown",
            attempt_number=next_attempt_number,
            score=score_percentage,
            skill_mastery=new_mastery,
            passed=passed,
            total_questions=len(valid_questions),
            correct_count=correct_count,
            created_at=result_record.created_at
        )

    @classmethod
    def get_learner_results(
        cls,
        db: Session,
        user_id: uuid.UUID,
        assessment_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[AssessmentHistoryItem]:
        """Fetch immutable historical assessment results for authenticated learner."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        skip = (page - 1) * page_size
        results = AssessmentRepository.get_learner_results(
            db=db,
            learner_id=profile.id,
            assessment_id=assessment_id,
            skip=skip,
            limit=page_size
        )

        history: List[AssessmentHistoryItem] = []
        for r in results:
            history.append(
                AssessmentHistoryItem(
                    id=r.id,
                    assessment_id=r.assessment_id,
                    assessment_title=r.assessment.title if r.assessment else "Unknown",
                    skill_name=r.assessment.skill.name if r.assessment and r.assessment.skill else "Unknown",
                    attempt_number=r.attempt_number,
                    score=float(r.score),
                    skill_mastery=float(r.skill_mastery),
                    passed=float(r.score) >= (float(r.assessment.passing_score) if r.assessment else 70.0),
                    created_at=r.created_at
                )
            )
        return history
