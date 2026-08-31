import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from backend.app.models.project import Project
from backend.app.models.project_skill import ProjectSkill


class ProjectRepository:
    """Repository handling database operations for practice projects."""

    @staticmethod
    def get_all(db: Session, skill_id: Optional[uuid.UUID] = None) -> List[Project]:
        """Fetch all projects with associated skills."""
        query = (
            select(Project)
            .options(
                selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
        )
        if skill_id:
            query = query.join(Project.project_skills).where(ProjectSkill.skill_id == skill_id)

        return db.execute(query).scalars().all()

    @staticmethod
    def get_by_id(db: Session, project_id: uuid.UUID) -> Optional[Project]:
        """Fetch project by ID with associated skills."""
        return db.execute(
            select(Project)
            .options(
                selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .where(Project.id == project_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_projects_for_skills(db: Session, skill_ids: List[uuid.UUID]) -> List[Project]:
        """Fetch projects that apply any of the specified skills."""
        if not skill_ids:
            return []

        return db.execute(
            select(Project)
            .options(
                selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .join(Project.project_skills)
            .where(ProjectSkill.skill_id.in_(skill_ids))
            .distinct()
        ).scalars().all()
