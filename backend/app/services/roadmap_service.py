import uuid
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundError, AuthorizationError, ConflictError, AppException
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.resource_skill import ResourceSkill
from backend.app.models.project_skill import ProjectSkill
from backend.app.repositories.learner_profile_repository import LearnerProfileRepository
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.repositories.resource_repository import ResourceRepository
from backend.app.repositories.project_repository import ProjectRepository
from backend.app.repositories.roadmap_repository import RoadmapRepository
from backend.app.services.skill_gap_service import SkillGapService
from backend.app.schemas.roadmap import (
    RoadmapResponse, RoadmapItemResponse, RoadmapSummaryResponse,
    SkillSummary, RoadmapGenerateRequest
)
from backend.app.schemas.recommendation import ResourceSummary, ProjectSummary


class RoadmapService:
    """Dependency-Aware, Deterministic, Explainable Roadmap Engine."""

    @classmethod
    def generate_roadmap(
        cls,
        db: Session,
        user_id: uuid.UUID,
        generate_in: Optional[RoadmapGenerateRequest] = None
    ) -> RoadmapResponse:
        """Generate a personalized, topologically-ordered learning roadmap."""
        # 1. Fetch learner profile
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        # 2. Determine target role
        target_role_id = (generate_in.target_role_id if generate_in and generate_in.target_role_id else profile.target_role_id)
        if not target_role_id:
            raise NotFoundError(
                message="No target role selected. Please set a target career role before generating a roadmap."
            )

        role = RoleRepository.get_by_id(db, target_role_id)
        if not role:
            raise NotFoundError(message="Target role does not exist", details={"role_id": str(target_role_id)})

        # Update profile target role if changed in request
        if profile.target_role_id != target_role_id:
            profile.target_role_id = target_role_id
            db.add(profile)
            db.flush()

        est_weeks = (
            generate_in.target_duration_weeks
            if generate_in and generate_in.target_duration_weeks
            else (profile.target_duration_weeks or 24)
        )

        # 3. Analyze real-time skill gaps
        gap_analysis = SkillGapService.analyze_gaps(db, user_id=user_id, override_role_id=target_role_id)
        gaps_by_skill = {item.skill_id: item for item in gap_analysis.skills}

        # Filter unmastered skills (only skills with gap > 0 need learning actions)
        unmastered_gap_skills = [s for s in gap_analysis.skills if s.gap > 0]
        unmastered_skill_ids = {s.skill_id for s in unmastered_gap_skills}

        # 4. Fetch learner's current proficiencies
        learner_skills = LearnerProfileRepository.get_learner_skills(db, profile.id)
        learner_proficiency: Dict[uuid.UUID, float] = {
            ls.skill_id: float(ls.proficiency) for ls in learner_skills
        }

        # 5. Build Dependency Graph with Per-Edge Strength Thresholds
        all_prereqs = SkillRepository.get_all_prerequisites(db)
        # prereqs_map: skill_id -> list of prerequisite_skill_id
        prereqs_map: Dict[uuid.UUID, List[uuid.UUID]] = defaultdict(list)
        prereq_names: Dict[uuid.UUID, List[str]] = defaultdict(list)
        prereq_thresholds: Dict[Tuple[uuid.UUID, uuid.UUID], float] = {}

        for p in all_prereqs:
            prereqs_map[p.skill_id].append(p.prerequisite_skill_id)
            if p.prerequisite_skill:
                prereq_names[p.skill_id].append(p.prerequisite_skill.name)
            # Per-edge threshold based on prerequisite edge strength and role target requirement
            role_target_prof = (
                gaps_by_skill[p.prerequisite_skill_id].required
                if p.prerequisite_skill_id in gaps_by_skill
                else 70.0
            )
            # Threshold = strength * target requirement (e.g. 1.0 * 80 = 80, 0.8 * 65 = 52)
            edge_threshold = round(float(p.strength) * role_target_prof, 2)
            prereq_thresholds[(p.skill_id, p.prerequisite_skill_id)] = edge_threshold

        # 6. Deterministic Topological Sort (Kahn's algorithm) with Strict Cycle Detection
        in_degree: Dict[uuid.UUID, int] = {}
        for s_id in unmastered_skill_ids:
            unmet_prereqs_count = 0
            for p_id in prereqs_map.get(s_id, []):
                req_threshold = prereq_thresholds.get((s_id, p_id), 70.0)
                if learner_proficiency.get(p_id, 0.0) < req_threshold:
                    unmet_prereqs_count += 1
            in_degree[s_id] = unmet_prereqs_count

        all_skills_map = {s.id: s for s in SkillRepository.get_all(db)}
        ordered_skill_ids: List[uuid.UUID] = []
        remaining_skill_ids = set(unmastered_skill_ids)

        while remaining_skill_ids:
            zero_in_degree = [s_id for s_id in remaining_skill_ids if in_degree[s_id] == 0]
            if zero_in_degree:
                # Deterministic tie breaking: importance DESC, gap DESC, name ASC
                zero_in_degree.sort(
                    key=lambda sid: (
                        gaps_by_skill[sid].importance,
                        gaps_by_skill[sid].gap,
                        gaps_by_skill[sid].skill
                    ),
                    reverse=True
                )
                chosen_id = zero_in_degree[0]
            else:
                # Strict Cycle Safety: Raise domain error when cycle is detected
                cycle_skills = [
                    all_skills_map[sid].name for sid in remaining_skill_ids if sid in all_skills_map
                ]
                raise AppException(
                    status_code=422,
                    code="ROADMAP_DEPENDENCY_CYCLE",
                    message=f"Dependency cycle detected in skill prerequisites involving: {', '.join(cycle_skills)}. Cannot generate a valid acyclic learning roadmap.",
                    details={"cyclic_skills": [str(sid) for sid in remaining_skill_ids]}
                )

            remaining_skill_ids.remove(chosen_id)
            ordered_skill_ids.append(chosen_id)

            # Reduce in-degree for dependent nodes
            for other_id in remaining_skill_ids:
                if chosen_id in prereqs_map.get(other_id, []):
                    in_degree[other_id] = max(0, in_degree[other_id] - 1)

        # 7. Create Roadmap & Versioning
        existing_active = RoadmapRepository.get_active_roadmap(db, profile.id)
        next_version = (existing_active.version + 1) if existing_active else 1

        RoadmapRepository.archive_previous_roadmaps(db, profile.id)

        new_roadmap = RoadmapRepository.create_roadmap(
            db=db,
            learner_id=profile.id,
            target_role_id=target_role_id,
            version=next_version,
            estimated_weeks=est_weeks
        )

        # 8. Create Roadmap Items for Ordered Skills
        all_resources = ResourceRepository.get_all(db)
        all_projects = ProjectRepository.get_all(db)

        res_by_skill = defaultdict(list)
        for r in all_resources:
            for rs in r.resource_skills:
                res_by_skill[rs.skill_id].append(r)

        proj_by_skill = defaultdict(list)
        for p in all_projects:
            for ps in p.project_skills:
                proj_by_skill[ps.skill_id].append(p)

        created_items: List[RoadmapItem] = []

        for seq, s_id in enumerate(ordered_skill_ids, start=1):
            skill_obj = all_skills_map.get(s_id)
            gap_item = gaps_by_skill.get(s_id)
            if not skill_obj or not gap_item:
                continue

            cand_resources = res_by_skill.get(s_id, [])
            selected_res = cand_resources[0] if cand_resources else None

            cand_projects = proj_by_skill.get(s_id, [])
            selected_proj = cand_projects[0] if cand_projects else None

            # Calculate prerequisite readiness using edge-specific threshold
            direct_prereqs = prereqs_map.get(s_id, [])
            unmet_prereq_names = []
            for p_id in direct_prereqs:
                req_threshold = prereq_thresholds.get((s_id, p_id), 70.0)
                p_prof = learner_proficiency.get(p_id, 0.0)
                if p_prof < req_threshold:
                    p_skill = all_skills_map.get(p_id)
                    if p_skill:
                        unmet_prereq_names.append(f"{p_skill.name} (>= {req_threshold:.0f}%)")

            if not unmet_prereq_names:
                item_status = "AVAILABLE"
                locked_reason = None
            else:
                item_status = "LOCKED"
                locked_reason = f"Requires prerequisite(s): {', '.join(unmet_prereq_names)}"

            # Explainability reason
            explanation = (
                f"Step {seq}: Learn {skill_obj.name} (Gap: {gap_item.gap:.0f}%, Importance: {gap_item.importance:.2f}). "
                + (f"Prerequisites met." if not unmet_prereq_names else f"Locked until {', '.join(unmet_prereq_names)} achieved.")
            )

            reason_payload = {
                "skill_gap": gap_item.gap,
                "importance": gap_item.importance,
                "prerequisites": prereq_names.get(s_id, []),
                "explanation": explanation
            }

            est_hours = (
                float(selected_res.estimated_minutes) / 60.0
                if selected_res and selected_res.estimated_minutes
                else (float(skill_obj.estimated_hours) if skill_obj.estimated_hours else 6.0)
            )

            r_item = RoadmapRepository.create_roadmap_item(
                db=db,
                roadmap_id=new_roadmap.id,
                sequence=seq,
                skill_id=s_id,
                resource_id=selected_res.id if selected_res else None,
                project_id=selected_proj.id if selected_proj else None,
                status=item_status,
                estimated_hours=round(est_hours, 2),
                reason=reason_payload,
                locked_reason=locked_reason
            )
            created_items.append(r_item)

        # Record Version Snapshot
        RoadmapRepository.create_version_history(
            db=db,
            roadmap_id=new_roadmap.id,
            version=next_version,
            trigger_type="initial_generation" if next_version == 1 else "recalculation",
            reason={"target_role": role.name, "total_steps": len(created_items)}
        )

        db.commit()

        # Reload complete roadmap with relations
        return cls.get_roadmap_response(db, new_roadmap.id)

    @classmethod
    def get_current_roadmap(cls, db: Session, user_id: uuid.UUID) -> RoadmapSummaryResponse:
        """Fetch current active roadmap summary and next best action."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        roadmap = RoadmapRepository.get_active_roadmap(db, profile.id)
        if not roadmap:
            raise NotFoundError(
                message="No active roadmap found. Please generate a roadmap first."
            )

        items_resp = [cls._serialize_roadmap_item(item) for item in roadmap.items]

        # Calculate metrics
        total = len(items_resp)
        completed = sum(1 for i in items_resp if i.status == "COMPLETED")
        in_progress = sum(1 for i in items_resp if i.status == "IN_PROGRESS")
        available = sum(1 for i in items_resp if i.status == "AVAILABLE")
        locked = sum(1 for i in items_resp if i.status == "LOCKED")
        overall_progress = round((completed / total) * 100.0, 2) if total > 0 else 0.0

        # Find Next Best Action: First IN_PROGRESS or AVAILABLE item
        next_action = next(
            (i for i in items_resp if i.status in ["IN_PROGRESS", "AVAILABLE"]),
            None
        )

        return RoadmapSummaryResponse(
            roadmap_id=roadmap.id,
            version=roadmap.version,
            status=roadmap.status,
            estimated_weeks=roadmap.estimated_weeks,
            total_items=total,
            completed_items=completed,
            in_progress_items=in_progress,
            available_items=available,
            locked_items=locked,
            overall_progress=overall_progress,
            next_best_action=next_action,
            items=items_resp
        )

    @classmethod
    def get_roadmap_by_id(cls, db: Session, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> RoadmapResponse:
        """Retrieve a specific roadmap by ID enforcing user ownership."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        roadmap = RoadmapRepository.get_by_id(db, roadmap_id)
        if not roadmap:
            raise NotFoundError(message="Roadmap not found")

        if roadmap.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this roadmap")

        return cls.get_roadmap_response(db, roadmap.id)

    @classmethod
    def get_roadmap_item_by_id(cls, db: Session, user_id: uuid.UUID, item_id: uuid.UUID) -> RoadmapItemResponse:
        """Retrieve a roadmap item by ID enforcing learner ownership."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        item = RoadmapRepository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundError(message="Roadmap item not found")

        if item.roadmap.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this roadmap item")

        return cls._serialize_roadmap_item(item)

    @classmethod
    def start_roadmap_item(cls, db: Session, user_id: uuid.UUID, item_id: uuid.UUID) -> RoadmapItemResponse:
        """Transition roadmap item from AVAILABLE -> IN_PROGRESS."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        item = RoadmapRepository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundError(message="Roadmap item not found")

        if item.roadmap.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this roadmap item")

        if item.status == "LOCKED":
            raise AppException(
                status_code=403,
                code="PREREQUISITE_NOT_MET",
                message=f"Cannot start locked roadmap item. {item.locked_reason or 'Prerequisites not met.'}"
            )

        if item.status == "COMPLETED":
            raise ConflictError(message="Roadmap item has already been completed.")

        item.status = "IN_PROGRESS"
        if item.progress == 0.0:
            item.progress = 25.0

        db.add(item)
        RoadmapRepository.record_progress(
            db=db,
            learner_id=profile.id,
            roadmap_item_id=item.id,
            status="IN_PROGRESS",
            percentage=float(item.progress)
        )
        db.commit()

        return cls._serialize_roadmap_item(item)

    @classmethod
    def complete_roadmap_item(cls, db: Session, user_id: uuid.UUID, item_id: uuid.UUID) -> RoadmapItemResponse:
        """Complete roadmap item, update progress, update learner skill mastery, and unlock dependent items."""
        profile = LearnerProfileRepository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundError(message="Learner profile not found")

        item = RoadmapRepository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundError(message="Roadmap item not found")

        if item.roadmap.learner_id != profile.id:
            raise AuthorizationError(message="Access forbidden to this roadmap item")

        if item.status == "LOCKED":
            raise AppException(
                status_code=403,
                code="PREREQUISITE_NOT_MET",
                message="Cannot complete locked item."
            )

        # Mark item completed
        item.status = "COMPLETED"
        item.progress = 100.0
        db.add(item)

        # Update progress record
        RoadmapRepository.record_progress(
            db=db,
            learner_id=profile.id,
            roadmap_item_id=item.id,
            status="COMPLETED",
            percentage=100.0
        )

        # If item has a skill, update learner skill mastery
        if item.skill_id:
            LearnerProfileRepository.add_or_update_learner_skill(
                db=db,
                learner_id=profile.id,
                skill_id=item.skill_id,
                proficiency=85.0,  # Mark as mastered on completion
                source="roadmap_completion",
                confidence=1.0
            )

        # Unlock dependent items in the same roadmap
        all_roadmap_items = db.query(RoadmapItem).filter(
            RoadmapItem.roadmap_id == item.roadmap_id,
            RoadmapItem.status == "LOCKED"
        ).all()

        if all_roadmap_items:
            # Refresh learner proficiencies
            updated_learner_skills = LearnerProfileRepository.get_learner_skills(db, profile.id)
            updated_profs = {ls.skill_id: float(ls.proficiency) for ls in updated_learner_skills}
            
            # Fetch target role requirements if exists
            target_role_id = item.roadmap.target_role_id if item.roadmap else None
            role_req_profs = {}
            if target_role_id:
                reqs = RoleRepository.get_role_skills(db, target_role_id)
                role_req_profs = {r.skill_id: float(r.required_proficiency) for r in reqs}

            all_prereqs = SkillRepository.get_all_prerequisites(db)
            prereqs_map = defaultdict(list)
            prereq_thresholds = {}
            for p in all_prereqs:
                prereqs_map[p.skill_id].append(p.prerequisite_skill_id)
                base_req = role_req_profs.get(p.prerequisite_skill_id, 70.0)
                prereq_thresholds[(p.skill_id, p.prerequisite_skill_id)] = round(float(p.strength) * base_req, 2)

            for locked_item in all_roadmap_items:
                if not locked_item.skill_id:
                    continue
                req_prereqs = prereqs_map.get(locked_item.skill_id, [])
                unmet = [
                    p for p in req_prereqs
                    if updated_profs.get(p, 0.0) < prereq_thresholds.get((locked_item.skill_id, p), 70.0)
                ]
                if not unmet:
                    locked_item.status = "AVAILABLE"
                    locked_item.locked_reason = None
                    db.add(locked_item)

        db.commit()
        return cls._serialize_roadmap_item(item)

    @classmethod
    def get_roadmap_response(cls, db: Session, roadmap_id: uuid.UUID) -> RoadmapResponse:
        """Helper to serialize full RoadmapResponse."""
        roadmap = RoadmapRepository.get_by_id(db, roadmap_id)
        if not roadmap:
            raise NotFoundError(message="Roadmap not found")

        items_resp = [cls._serialize_roadmap_item(item) for item in roadmap.items]

        return RoadmapResponse(
            id=roadmap.id,
            target_role_id=roadmap.target_role_id,
            target_role_name=roadmap.target_role.name if roadmap.target_role else None,
            version=roadmap.version,
            status=roadmap.status,
            estimated_weeks=roadmap.estimated_weeks,
            items=items_resp,
            created_at=roadmap.created_at
        )

    @staticmethod
    def _serialize_roadmap_item(item: RoadmapItem) -> RoadmapItemResponse:
        """Serialize RoadmapItem ORM object into RoadmapItemResponse schema."""
        skill_summary = None
        if item.skill:
            skill_summary = SkillSummary(
                id=item.skill.id,
                name=item.skill.name,
                slug=item.skill.slug,
                category=item.skill.category
            )

        res_summary = None
        if item.resource:
            skills_covered = [
                rs.skill.name for rs in item.resource.resource_skills if rs.skill
            ] if hasattr(item.resource, "resource_skills") and item.resource.resource_skills else []
            res_summary = ResourceSummary(
                id=item.resource.id,
                title=item.resource.title,
                url=item.resource.url,
                resource_type=item.resource.resource_type,
                provider=item.resource.provider,
                difficulty=item.resource.difficulty,
                estimated_hours=round(float(item.resource.estimated_minutes) / 60.0, 2) if item.resource.estimated_minutes else None,
                quality_score=float(item.resource.quality_score) if item.resource.quality_score else None,
                is_free=bool(item.resource.meta_data.get("is_free", True)) if isinstance(item.resource.meta_data, dict) else True,
                skills_covered=skills_covered
            )

        proj_summary = None
        if item.project:
            proj_summary = ProjectSummary(
                id=item.project.id,
                title=item.project.title,
                description=item.project.description,
                difficulty=item.project.difficulty,
                estimated_hours=float(item.project.estimated_hours) if item.project.estimated_hours else None,
                skills_covered=[ps.skill.name for ps in item.project.project_skills if ps.skill] if hasattr(item.project, "project_skills") and item.project.project_skills else []
            )

        return RoadmapItemResponse(
            id=item.id,
            roadmap_id=item.roadmap_id,
            sequence=item.sequence,
            skill=skill_summary,
            resource=res_summary,
            project=proj_summary,
            assessment=None,
            status=item.status,
            progress=float(item.progress),
            estimated_hours=float(item.estimated_hours) if item.estimated_hours else None,
            reason=item.reason if isinstance(item.reason, dict) else {},
            locked_reason=item.locked_reason,
            created_at=item.created_at
        )
