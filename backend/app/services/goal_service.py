import uuid
import re
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.role import Role
from backend.app.models.skill import Skill
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.skill_repository import SkillRepository
from backend.app.ai.providers.base import LLMProvider
from backend.app.ai.providers.factory import get_llm_provider
from backend.app.ai.prompts.goal_prompts import (
    GOAL_EXTRACTION_SYSTEM_PROMPT,
    GOAL_EXTRACTION_USER_PROMPT_TEMPLATE
)
from backend.app.schemas.goal import (
    LLMGoalExtractionCandidate,
    ExtractedSkillItem,
    SuggestedRoleItem,
    GoalAnalysisData
)


class GoalService:
    """Deterministic AI Goal Understanding & Catalog Grounding Service.

    Coordinates between LLM structured extraction, strict Pydantic validation,
    and PostgreSQL catalog grounding. Never allows the LLM to assign arbitrary
    UUIDs, authoritative proficiencies, or direct roadmap modifications.
    """

    # Approved role aliases mapping to canonical role slugs in DB
    ROLE_ALIAS_MAP: Dict[str, str] = {
        "ml engineer": "ai-ml-engineer",
        "machine learning engineer": "ai-ml-engineer",
        "machine learning": "ai-ml-engineer",
        "machine learning engineering": "ai-ml-engineer",
        "ai engineer": "ai-ml-engineer",
        "ai/ml engineer": "ai-ml-engineer",
        "ai/ml": "ai-ml-engineer",
        "data scientist": "data-scientist",
        "data science": "data-scientist",
        "data engineer": "data-engineer",
        "data engineering": "data-engineer",
        "backend developer": "backend-developer",
        "backend engineer": "backend-developer",
        "backend dev": "backend-developer",
        "backend": "backend-developer",
        "frontend developer": "frontend-developer",
        "frontend engineer": "frontend-developer",
        "frontend": "frontend-developer",
        "full stack developer": "full-stack-developer",
        "fullstack developer": "full-stack-developer",
        "full stack": "full-stack-developer",
        "cloud engineer": "cloud-devops-engineer",
        "devops engineer": "cloud-devops-engineer",
        "devops": "cloud-devops-engineer",
        "security engineer": "security-engineer",
        "cybersecurity engineer": "security-engineer",
    }

    # Approved skill aliases mapping to canonical skill slugs in DB
    SKILL_ALIAS_MAP: Dict[str, str] = {
        "python": "python",
        "python 3": "python",
        "sql": "sql",
        "postgresql": "sql",
        "mysql": "sql",
        "statistics": "statistics",
        "probability": "probability",
        "stats": "statistics",
        "machine learning": "machine-learning",
        "ml": "machine-learning",
        "deep learning": "deep-learning",
        "dl": "deep-learning",
        "neural networks": "deep-learning",
        "data processing": "data-processing",
        "data cleaning": "data-processing",
        "data wrangling": "data-processing",
        "mlops": "mlops",
        "model deployment": "mlops",
        "model evaluation": "model-evaluation",
        "model metrics": "model-evaluation",
        "fastapi": "fastapi",
        "docker": "docker",
        "git": "git",
        "github": "git",
        "pytorch": "pytorch",
        "tensorflow": "deep-learning",
        "scikit-learn": "machine-learning",
        "pandas": "data-processing",
        "numpy": "data-processing"
    }

    @classmethod
    def analyze_goal(
        cls,
        db: Session,
        goal_text: str,
        provider: Optional[LLMProvider] = None
    ) -> GoalAnalysisData:
        """Analyze natural language goal text, ground candidates against DB catalogs,

        and return normalized, validated structured goal information.
        """
        provider = provider or get_llm_provider()

        # Build prompt
        formatted_prompt = GOAL_EXTRACTION_USER_PROMPT_TEMPLATE.format(goal_text=goal_text)

        # Call LLM Provider with structured output constraint
        candidate = cls._extract_candidate_safely(provider, formatted_prompt, goal_text)

        # Ground extracted role against database catalog
        role_match, suggested_roles, role_status = cls._ground_role(db, candidate.target_role, goal_text)

        # Ground extracted skills against database catalog
        grounded_skills, technologies = cls._ground_skills(
            db,
            candidate.known_skills + candidate.technologies
        )

        # Normalize duration & study time
        normalized_weeks = cls._normalize_weeks(candidate.timeline_weeks)
        normalized_hours = cls._normalize_daily_hours(candidate.daily_study_hours)

        # Compute missing information
        missing_info = []
        if not role_match and role_status != "AMBIGUOUS":
            missing_info.append("target_role")
        if normalized_weeks is None:
            missing_info.append("timeline_weeks")
        if normalized_hours is None:
            missing_info.append("daily_study_hours")
        if not candidate.experience_level:
            missing_info.append("experience_level")

        # Determine overall extraction status and confidence
        overall_status, overall_confidence, clarification_prompt = cls._determine_status_and_confidence(
            role_status=role_status,
            role_match=role_match,
            candidate_confidence=candidate.confidence,
            suggested_roles=suggested_roles,
            grounded_skills=grounded_skills,
            missing_info=missing_info,
            target_role_name=candidate.target_role
        )

        return GoalAnalysisData(
            raw_goal=goal_text,
            target_role=role_match.name if role_match else candidate.target_role,
            role_id=role_match.id if role_match else None,
            role_slug=role_match.slug if role_match else None,
            role_confidence=0.95 if role_match else (0.50 if role_status == "AMBIGUOUS" else 0.0),
            timeline_weeks=normalized_weeks,
            daily_study_hours=normalized_hours,
            experience_level=candidate.experience_level,
            known_skills=grounded_skills,
            technologies=technologies,
            preferences=candidate.preferences,
            confidence=round(overall_confidence, 2),
            status=overall_status,
            missing_information=missing_info,
            clarification_prompt=clarification_prompt,
            suggested_roles=suggested_roles
        )

    @classmethod
    def _extract_candidate_safely(
        cls,
        provider: LLMProvider,
        prompt: str,
        raw_text: str
    ) -> LLMGoalExtractionCandidate:
        """Call provider asynchronously with deterministic fallback on failure."""
        try:
            import concurrent.futures

            def _run():
                return asyncio.run(
                    provider.generate_structured(
                        prompt=prompt,
                        response_schema=LLMGoalExtractionCandidate,
                        system_prompt=GOAL_EXTRACTION_SYSTEM_PROMPT
                    )
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run)
                candidate = future.result(timeout=10.0)

            return candidate
        except Exception:
            # Fallback to deterministic regex-based extraction if provider fails
            from backend.app.ai.providers.mock_provider import MockLLMProvider
            fallback_provider = MockLLMProvider()
            return fallback_provider._extract_goal_candidate(raw_text)

    @classmethod
    def _ground_role(
        cls,
        db: Session,
        raw_role: Optional[str],
        raw_text: str
    ) -> Tuple[Optional[Role], List[SuggestedRoleItem], str]:
        """Ground extracted role against PostgreSQL roles catalog."""
        all_roles = RoleRepository.get_all(db)
        roles_by_slug = {r.slug: r for r in all_roles}
        roles_by_name_lower = {r.name.lower(): r for r in all_roles}

        text_lower = raw_text.lower()
        role_lower = (raw_role or "").lower().strip()

        # Ambiguity Checks:
        # "work in AI" / "into AI" matches AI/ML Engineer and Data Scientist
        if role_lower == "ai" or "work in ai" in text_lower or "into ai" in text_lower or "career in ai" in text_lower:
            aiml_role = roles_by_slug.get("ai-ml-engineer")
            ds_role = roles_by_slug.get("data-scientist")
            suggested = []
            if aiml_role:
                suggested.append(SuggestedRoleItem(id=aiml_role.id, name=aiml_role.name, slug=aiml_role.slug, match_score=0.90))
            if ds_role:
                suggested.append(SuggestedRoleItem(id=ds_role.id, name=ds_role.name, slug=ds_role.slug, match_score=0.85))
            return None, suggested, "AMBIGUOUS"

        # "work with data" / "data career" matches Data Scientist and Data Analyst
        if "work with data" in text_lower or "career in data" in text_lower or "data career" in text_lower:
            ds_role = roles_by_slug.get("data-scientist")
            da_role = roles_by_slug.get("data-analyst")
            suggested = []
            if ds_role:
                suggested.append(SuggestedRoleItem(id=ds_role.id, name=ds_role.name, slug=ds_role.slug, match_score=0.90))
            if da_role:
                suggested.append(SuggestedRoleItem(id=da_role.id, name=da_role.name, slug=da_role.slug, match_score=0.85))
            return None, suggested, "AMBIGUOUS"

        # "software career" / "build software" matches Backend, Frontend, and Full Stack Developer
        if "software career" in text_lower or "software engineering" in text_lower or "build software" in text_lower:
            be_role = roles_by_slug.get("backend-developer")
            fs_role = roles_by_slug.get("full-stack-developer")
            fe_role = roles_by_slug.get("frontend-developer")
            suggested = []
            if be_role:
                suggested.append(SuggestedRoleItem(id=be_role.id, name=be_role.name, slug=be_role.slug, match_score=0.85))
            if fs_role:
                suggested.append(SuggestedRoleItem(id=fs_role.id, name=fs_role.name, slug=fs_role.slug, match_score=0.85))
            if fe_role:
                suggested.append(SuggestedRoleItem(id=fe_role.id, name=fe_role.name, slug=fe_role.slug, match_score=0.80))
            return None, suggested, "AMBIGUOUS"

        # 1. Check direct alias mapping
        if role_lower in cls.ROLE_ALIAS_MAP:
            slug = cls.ROLE_ALIAS_MAP[role_lower]
            if slug in roles_by_slug:
                return roles_by_slug[slug], [], "RESOLVED"

        # 2. Check exact name match
        if role_lower in roles_by_name_lower:
            return roles_by_name_lower[role_lower], [], "RESOLVED"

        # 3. Check substring in role names
        matches = []
        for r in all_roles:
            r_name = r.name.lower()
            if role_lower and (role_lower in r_name or r_name in role_lower):
                matches.append(r)
            elif any(part in r_name for part in role_lower.split() if len(part) > 3):
                matches.append(r)

        if len(matches) == 1:
            return matches[0], [], "RESOLVED"
        elif len(matches) > 1:
            suggested = [
                SuggestedRoleItem(id=r.id, name=r.name, slug=r.slug, match_score=0.80)
                for r in matches[:3]
            ]
            return None, suggested, "AMBIGUOUS"

        # 4. Unknown role
        if raw_role:
            # Suggest all catalog roles
            suggested = [
                SuggestedRoleItem(id=r.id, name=r.name, slug=r.slug, match_score=0.50)
                for r in all_roles[:4]
            ]
            return None, suggested, "UNRESOLVED"

        return None, [], "CLARIFICATION_REQUIRED"

    @classmethod
    def _ground_skills(
        cls,
        db: Session,
        raw_skill_names: List[str]
    ) -> Tuple[List[ExtractedSkillItem], List[str]]:
        """Ground extracted skills against PostgreSQL skills catalog."""
        all_skills = SkillRepository.get_all(db)
        skills_by_slug = {s.slug: s for s in all_skills}
        skills_by_name_lower = {s.name.lower(): s for s in all_skills}

        grounded_skills: List[ExtractedSkillItem] = []
        technologies: List[str] = []
        seen_skill_ids = set()

        for raw_name in raw_skill_names:
            clean_name = raw_name.strip()
            if not clean_name:
                continue

            lower_name = clean_name.lower()
            matched_skill: Optional[Skill] = None

            # 1. Alias lookup
            if lower_name in cls.SKILL_ALIAS_MAP:
                slug = cls.SKILL_ALIAS_MAP[lower_name]
                matched_skill = skills_by_slug.get(slug)

            # 2. Exact lower name lookup
            if not matched_skill and lower_name in skills_by_name_lower:
                matched_skill = skills_by_name_lower[lower_name]

            # 3. Substring lookup
            if not matched_skill:
                for s in all_skills:
                    if lower_name in s.name.lower() or s.name.lower() in lower_name:
                        matched_skill = s
                        break

            if matched_skill:
                if matched_skill.id not in seen_skill_ids:
                    seen_skill_ids.add(matched_skill.id)
                    grounded_skills.append(
                        ExtractedSkillItem(
                            name=clean_name,
                            matched_name=matched_skill.name,
                            skill_id=matched_skill.id,
                            confidence=0.95,
                            status="CONFIRMED"
                        )
                    )
                    technologies.append(matched_skill.name)
            else:
                grounded_skills.append(
                    ExtractedSkillItem(
                        name=clean_name,
                        matched_name=None,
                        skill_id=None,
                        confidence=0.50,
                        status="UNRESOLVED"
                    )
                )
                technologies.append(clean_name)

        return grounded_skills, list(dict.fromkeys(technologies))

    @staticmethod
    def _normalize_weeks(val: Optional[int]) -> Optional[int]:
        if val is None:
            return None
        try:
            w = int(val)
            if 1 <= w <= 156:  # 1 week to 3 years
                return w
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def _normalize_daily_hours(val: Optional[float]) -> Optional[float]:
        if val is None:
            return None
        try:
            h = float(val)
            if 0.1 <= h <= 24.0:
                return round(h, 1)
        except (ValueError, TypeError):
            pass
        return None

    @classmethod
    def _determine_status_and_confidence(
        cls,
        role_status: str,
        role_match: Optional[Role],
        candidate_confidence: float,
        suggested_roles: List[SuggestedRoleItem],
        grounded_skills: List[ExtractedSkillItem],
        missing_info: List[str],
        target_role_name: Optional[str]
    ) -> Tuple[str, float, Optional[str]]:
        """Compute authoritative extraction status and overall confidence."""
        if role_status == "AMBIGUOUS":
            clarification = (
                "Your goal indicates an interest in multiple career paths. "
                "Please select your preferred target role from the suggested options."
            )
            return "AMBIGUOUS", 0.50, clarification

        if role_status == "UNRESOLVED":
            role_str = f"'{target_role_name}'" if target_role_name else "specified"
            clarification = (
                f"The career role {role_str} could not be matched directly to our catalog. "
                "Please select a related standard career path."
            )
            return "UNRESOLVED", 0.20, clarification

        if role_status == "CLARIFICATION_REQUIRED" or not role_match:
            clarification = "Please specify a target career role (e.g. AI/ML Engineer, Data Scientist, Backend Developer)."
            return "CLARIFICATION_REQUIRED", 0.30, clarification

        # Resolved Role:
        score = 0.85
        if grounded_skills:
            score += 0.10
        if len(missing_info) <= 1:
            score += 0.05

        return "RESOLVED", min(1.0, score), None
