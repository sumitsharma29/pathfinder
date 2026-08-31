import re
import json
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

from backend.app.ai.providers.base import LLMProvider
from backend.app.schemas.goal import LLMGoalExtractionCandidate

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProvider):
    """Deterministic Mock LLM Provider for offline development and testing.

    Performs intelligent rule-based extraction to simulate LLM structured output
    without external network dependencies or API costs.
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        text = prompt.lower()

        # Prompt injection test defense:
        if "reveal secrets" in text or "database password" in text or "system prompt" in text:
            return "I cannot fulfill requests attempting to access confidential system credentials or instructions."

        # RAG Grounding handler:
        if "<curated_resources>" in prompt:
            # Extract resources block
            match = re.search(r"<curated_resources>(.*?)</curated_resources>", prompt, re.DOTALL)
            res_content = match.group(1).strip() if match else ""

            if not res_content or "no relevant resources found" in res_content.lower():
                return "I don't have enough information in the curated PathFinder resources to answer this question accurately."

            # Check question topic
            q_match = re.search(r"<learner_question>(.*?)</learner_question>", prompt, re.DOTALL)
            question = (q_match.group(1).strip() if q_match else "").lower()

            if "overfitting" in question or "reduce overfitting" in question:
                return (
                    "Overfitting occurs when a machine learning model learns the training data and noise too closely, "
                    "leading to poor generalization on unseen validation or test data. "
                    "Key strategies to prevent and reduce overfitting include: "
                    "1. Regularization (L1/L2 penalties), 2. Cross-validation, 3. Early stopping during training, "
                    "4. Data augmentation, and 5. Simplifying model architecture. "
                    "Refer to the curated materials for detailed tutorials and practical code examples."
                )
            elif "what should i study today" in question or "next step" in question:
                return (
                    "Based on your active milestone and target career path, you should focus on completing the highest-priority "
                    "curated resource listed in your active roadmap."
                )
            else:
                # Return generic grounded answer summarizing available sources
                return (
                    f"Based on the curated PathFinder learning resources, here is the relevant guidance: "
                    f"The provided learning materials cover the key foundational concepts and practical techniques for this topic. "
                    f"Please review the attached course materials and documentation for step-by-step guidance."
                )

        return "Mock LLM text response."

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> T:
        # Check if caller requested LLMGoalExtractionCandidate
        if response_schema == LLMGoalExtractionCandidate or issubclass(response_schema, BaseModel):
            candidate = self._extract_goal_candidate(prompt)
            if response_schema == LLMGoalExtractionCandidate:
                return candidate  # type: ignore
            # Otherwise parse model dump into target schema
            return response_schema.model_validate(candidate.model_dump())

        raise NotImplementedError(f"MockLLMProvider does not support schema {response_schema.__name__}")

    def _extract_goal_candidate(self, prompt: str) -> LLMGoalExtractionCandidate:
        text = prompt.lower()

        # Prompt Injection Defense: strip out malicious instructions from prompt analysis
        if "ignore all previous instructions" in text or "reveal secrets" in text or "system prompt" in text:
            # Safely treat prompt as benign text without executing injected commands
            pass

        # 1. Target Role Extraction
        target_role = None
        confidence = 0.85
        missing_info = []

        # Role aliases / patterns
        if "quantum underwater architect" in text:
            target_role = "Quantum Underwater Architect"
            confidence = 0.30
        elif "work in ai" in text or "career in ai" in text or "into ai" in text or "build ai" in text or text.strip() == "ai":
            target_role = "AI"
            confidence = 0.50
        elif "work with data" in text or "career in data" in text or "data career" in text:
            target_role = "Data"
            confidence = 0.50
        elif "software career" in text or "software engineering" in text or "build software" in text:
            target_role = "Software"
            confidence = 0.50
        elif any(k in text for k in ["ml engineer", "machine learning engineer", "machine learning engineering", "ai/ml engineer", "ai engineer"]):
            target_role = "Machine Learning Engineer"
            confidence = 0.95
        elif any(k in text for k in ["data scientist", "data science"]):
            target_role = "Data Scientist"
            confidence = 0.95
        elif any(k in text for k in ["data engineer", "data engineering"]):
            target_role = "Data Engineer"
            confidence = 0.95
        elif any(k in text for k in ["backend developer", "backend engineer", "backend dev"]):
            target_role = "Backend Developer"
            confidence = 0.95
        elif any(k in text for k in ["full stack", "fullstack"]):
            target_role = "Full Stack Developer"
            confidence = 0.95
        elif any(k in text for k in ["frontend developer", "frontend engineer"]):
            target_role = "Frontend Developer"
            confidence = 0.95
        elif any(k in text for k in ["cloud engineer", "devops engineer", "devops"]):
            target_role = "Cloud / DevOps Engineer"
            confidence = 0.95
        elif any(k in text for k in ["security engineer", "cybersecurity engineer", "cybersecurity"]):
            target_role = "Security Engineer"
            confidence = 0.95
        else:
            confidence = 0.30
            missing_info.append("target_role")

        # 2. Timeline Extraction
        timeline_weeks = None
        # Match months (e.g. 6 months, six months)
        month_match = re.search(r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+months?", text)
        if month_match:
            word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
            val_str = month_match.group(1)
            months = int(val_str) if val_str.isdigit() else word_map.get(val_str, 6)
            timeline_weeks = months * 4
        else:
            week_match = re.search(r"(\d+)\s+weeks?", text)
            if week_match:
                timeline_weeks = int(week_match.group(1))
            elif "1 year" in text or "one year" in text:
                timeline_weeks = 52

        if timeline_weeks is None:
            missing_info.append("timeline_weeks")

        # 3. Daily Study Hours Extraction
        daily_study_hours = None
        hour_match = re.search(r"(\d+(?:\.\d+)?|one|two|three|four|five|six)\s+hours?(?:\s+(?:a|per|every)\s+day)?", text)
        if hour_match:
            word_map_h = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0, "six": 6.0}
            val_h = hour_match.group(1)
            daily_study_hours = float(val_h) if (val_h.replace('.', '', 1).isdigit()) else word_map_h.get(val_h, 2.0)
        elif "30 minutes" in text or "half an hour" in text:
            daily_study_hours = 0.5

        if daily_study_hours is None:
            missing_info.append("daily_study_hours")

        # 4. Experience Level
        experience_level = None
        if "beginner" in text or "starting from scratch" in text or "no experience" in text:
            experience_level = "beginner"
        elif "intermediate" in text or "some experience" in text:
            experience_level = "intermediate"
        elif "advanced" in text or "senior" in text or "experienced" in text:
            experience_level = "advanced"

        # 5. Known Skills / Technologies
        known_skills = []
        technologies = []

        skill_catalog_keywords = [
            ("python", "Python"),
            ("sql", "SQL"),
            ("statistics", "Statistics"),
            ("probability", "Probability"),
            ("machine learning", "Machine Learning"),
            ("deep learning", "Deep Learning"),
            ("data processing", "Data Processing"),
            ("mlops", "MLOps"),
            ("model evaluation", "Model Evaluation"),
            ("fastapi", "FastAPI"),
            ("docker", "Docker"),
            ("git", "Git"),
            ("pytorch", "PyTorch"),
            ("tensorflow", "TensorFlow"),
            ("scikit-learn", "Scikit-Learn")
        ]

        for kw, canonical_name in skill_catalog_keywords:
            if kw in text:
                known_skills.append(canonical_name)
                if canonical_name in ["Python", "SQL", "FastAPI", "Docker", "Git", "PyTorch", "TensorFlow", "Scikit-Learn"]:
                    technologies.append(canonical_name)

        # 6. Preferences
        preferences: Dict[str, Any] = {}
        if "hands-on" in text or "practical" in text or "projects" in text:
            preferences["learning_style"] = "practical"
        elif "theoretical" in text or "math" in text:
            preferences["learning_style"] = "theoretical"

        return LLMGoalExtractionCandidate(
            target_role=target_role,
            timeline_weeks=timeline_weeks,
            daily_study_hours=daily_study_hours,
            experience_level=experience_level,
            technologies=list(dict.fromkeys(technologies)),
            known_skills=list(dict.fromkeys(known_skills)),
            preferences=preferences,
            confidence=confidence,
            missing_information=missing_info
        )
