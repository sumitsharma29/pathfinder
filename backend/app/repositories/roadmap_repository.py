import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session, joinedload, selectinload
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.roadmap_version import RoadmapVersion
from backend.app.models.progress import Progress
from backend.app.models.resource import Resource
from backend.app.models.project import Project
from backend.app.models.resource_skill import ResourceSkill
from backend.app.models.project_skill import ProjectSkill


class RoadmapRepository:
    """Repository handling database operations for Roadmaps, RoadmapItems, Versions, and Progress."""

    @staticmethod
    def get_active_roadmap(db: Session, learner_id: uuid.UUID) -> Optional[Roadmap]:
        """Fetch current active roadmap for learner with all eager relations."""
        return db.execute(
            select(Roadmap)
            .options(
                joinedload(Roadmap.target_role),
                selectinload(Roadmap.items).joinedload(RoadmapItem.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.resource).selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.project).selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .where(Roadmap.learner_id == learner_id, Roadmap.status == "active")
            .order_by(desc(Roadmap.version))
        ).scalars().first()

    @staticmethod
    def get_by_id(db: Session, roadmap_id: uuid.UUID) -> Optional[Roadmap]:
        """Fetch roadmap by ID with items."""
        return db.execute(
            select(Roadmap)
            .options(
                joinedload(Roadmap.target_role),
                selectinload(Roadmap.items).joinedload(RoadmapItem.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.resource).selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill),
                selectinload(Roadmap.items).joinedload(RoadmapItem.project).selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .where(Roadmap.id == roadmap_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_item_by_id(db: Session, item_id: uuid.UUID) -> Optional[RoadmapItem]:
        """Fetch single roadmap item with roadmap, skill, resource, and project relations."""
        return db.execute(
            select(RoadmapItem)
            .options(
                joinedload(RoadmapItem.roadmap),
                joinedload(RoadmapItem.skill),
                joinedload(RoadmapItem.resource).selectinload(Resource.resource_skills).joinedload(ResourceSkill.skill),
                joinedload(RoadmapItem.project).selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .where(RoadmapItem.id == item_id)
        ).scalar_one_or_none()

    @staticmethod
    def create_roadmap(
        db: Session,
        learner_id: uuid.UUID,
        target_role_id: uuid.UUID,
        version: int = 1,
        estimated_weeks: Optional[int] = 24
    ) -> Roadmap:
        """Create a new active roadmap."""
        roadmap = Roadmap(
            learner_id=learner_id,
            target_role_id=target_role_id,
            version=version,
            status="active",
            estimated_weeks=estimated_weeks
        )
        db.add(roadmap)
        db.flush()
        return roadmap

    @staticmethod
    def create_roadmap_item(
        db: Session,
        roadmap_id: uuid.UUID,
        sequence: int,
        skill_id: Optional[uuid.UUID],
        resource_id: Optional[uuid.UUID],
        project_id: Optional[uuid.UUID],
        status: str,
        estimated_hours: Optional[float],
        reason: Optional[dict] = None,
        locked_reason: Optional[str] = None
    ) -> RoadmapItem:
        """Create an item within a roadmap."""
        item = RoadmapItem(
            roadmap_id=roadmap_id,
            sequence=sequence,
            skill_id=skill_id,
            resource_id=resource_id,
            project_id=project_id,
            status=status,
            progress=0.0,
            estimated_hours=estimated_hours,
            reason=reason or {},
            locked_reason=locked_reason
        )
        db.add(item)
        db.flush()
        return item

    @staticmethod
    def archive_previous_roadmaps(db: Session, learner_id: uuid.UUID) -> None:
        """Mark previous active roadmaps as archived when regenerating."""
        active_roadmaps = db.execute(
            select(Roadmap).where(Roadmap.learner_id == learner_id, Roadmap.status == "active")
        ).scalars().all()
        for r in active_roadmaps:
            r.status = "archived"
        db.flush()

    @staticmethod
    def create_version_history(
        db: Session,
        roadmap_id: uuid.UUID,
        version: int,
        trigger_type: str,
        reason: Optional[dict] = None
    ) -> RoadmapVersion:
        """Record version history snapshot."""
        rv = RoadmapVersion(
            roadmap_id=roadmap_id,
            version=version,
            trigger_type=trigger_type,
            reason=reason or {}
        )
        db.add(rv)
        db.flush()
        return rv

    @staticmethod
    def record_progress(
        db: Session,
        learner_id: uuid.UUID,
        roadmap_item_id: uuid.UUID,
        status: str,
        percentage: float
    ) -> Progress:
        """Record or update progress on a roadmap item."""
        p = db.execute(
            select(Progress).where(
                Progress.learner_id == learner_id,
                Progress.roadmap_item_id == roadmap_item_id
            )
        ).scalar_one_or_none()

        now_utc = datetime.now(timezone.utc)

        if not p:
            p = Progress(
                learner_id=learner_id,
                roadmap_item_id=roadmap_item_id,
                status=status,
                percentage=percentage,
                started_at=now_utc if status in ["IN_PROGRESS", "COMPLETED"] else None,
                completed_at=now_utc if status == "COMPLETED" else None,
                time_spent_minutes=0
            )
            db.add(p)
        else:
            p.status = status
            p.percentage = percentage
            if status == "IN_PROGRESS" and not p.started_at:
                p.started_at = now_utc
            elif status == "COMPLETED":
                p.completed_at = now_utc
                p.percentage = 100.0

        db.flush()
        return p
