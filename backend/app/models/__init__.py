from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.skill import Skill
from backend.app.models.role import Role
from backend.app.models.role_skill import RoleSkill
from backend.app.models.learner_skill import LearnerSkill
from backend.app.models.skill_prerequisite import SkillPrerequisite
from backend.app.models.resource import Resource
from backend.app.models.resource_skill import ResourceSkill
from backend.app.models.project import Project
from backend.app.models.project_skill import ProjectSkill
from backend.app.models.assessment import Assessment
from backend.app.models.assessment_question import AssessmentQuestion
from backend.app.models.assessment_result import AssessmentResult
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.recommendation import Recommendation
from backend.app.models.feedback import Feedback
from backend.app.models.progress import Progress
from backend.app.models.conversation import Conversation
from backend.app.models.conversation_message import ConversationMessage
from backend.app.models.roadmap_version import RoadmapVersion

__all__ = [
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "User",
    "LearnerProfile",
    "Skill",
    "Role",
    "RoleSkill",
    "LearnerSkill",
    "SkillPrerequisite",
    "Resource",
    "ResourceSkill",
    "Project",
    "ProjectSkill",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentResult",
    "Roadmap",
    "RoadmapItem",
    "Recommendation",
    "Feedback",
    "Progress",
    "Conversation",
    "ConversationMessage",
    "RoadmapVersion",
]
