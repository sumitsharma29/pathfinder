from backend.app.schemas.common import APIResponse, ErrorDetail, MessageResponse
from backend.app.schemas.auth import (
    RegisterRequest, LoginRequest, UserResponse,
    AuthData, AuthResponse, UserMeResponse
)
from backend.app.schemas.profile import (
    LearnerProfileResponse, LearnerProfileUpdateRequest,
    LearnerSkillCreateRequest, LearnerSkillUpdateRequest,
    LearnerSkillItemResponse, TargetRoleSummary
)
from backend.app.schemas.skill import (
    SkillResponse, SkillPrerequisiteResponse, SkillDetailResponse
)
from backend.app.schemas.role import (
    RoleResponse, RoleSkillRequirementResponse, RoleDetailResponse
)
from backend.app.schemas.skill_gap import (
    SkillGapItem, SkillGapSummary, SkillGapAnalysisData, SkillGapResponse
)
from backend.app.schemas.recommendation import (
    RecommendationReason, ResourceSummary, ProjectSummary,
    RecommendationItem, RecommendationListResponse,
    RecommendationDetailResponse, FeedbackCreateRequest, FeedbackResponse
)
from backend.app.schemas.roadmap import (
    RoadmapGenerateRequest, RoadmapResponse,
    RoadmapItemResponse, RoadmapSummaryResponse, SkillSummary
)
from backend.app.schemas.assessment import (
    AssessmentQuestionPublic, AssessmentSummary, AssessmentDetailResponse,
    AnswerSubmissionItem, AssessmentSubmissionRequest,
    AssessmentResultResponse, AssessmentHistoryItem
)
from backend.app.schemas.adaptive import (
    AdaptiveIntervention, NextBestActionResponse,
    AdaptiveEvaluationRequest, AdaptiveEvaluationResponse
)
from backend.app.schemas.goal import (
    GoalAnalysisRequest, LLMGoalExtractionCandidate,
    ExtractedSkillItem, SuggestedRoleItem, GoalAnalysisData
)
from backend.app.schemas.rag import (
    RetrievedResourceSource, RAGQueryRequest, RAGAnswerResponse
)
from backend.app.schemas.assistant import (
    AssistantChatRequest, AssistantMessageItem, AssistantChatData,
    ConversationSummary, ConversationDetailData
)
from backend.app.schemas.progress import (
    OverallProgressResponse, SkillProgressItem, MilestoneProgressItem,
    MilestoneSummary, DashboardOverview, DashboardCompletedMetrics,
    DashboardWeakAreas, DashboardLearningFocus, DashboardAggregationResponse
)
from backend.app.schemas.resource import (
    ResourceItemResponse, ResourceDetailResponse, PaginatedResourcesResponse, ResourceSkillSummary
)

__all__ = [
    "APIResponse",
    "ErrorDetail",
    "MessageResponse",
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "AuthData",
    "AuthResponse",
    "UserMeResponse",
    "LearnerProfileResponse",
    "LearnerProfileUpdateRequest",
    "LearnerSkillCreateRequest",
    "LearnerSkillUpdateRequest",
    "LearnerSkillItemResponse",
    "TargetRoleSummary",
    "SkillResponse",
    "SkillPrerequisiteResponse",
    "SkillDetailResponse",
    "RoleResponse",
    "RoleSkillRequirementResponse",
    "RoleDetailResponse",
    "SkillGapItem",
    "SkillGapSummary",
    "SkillGapAnalysisData",
    "SkillGapResponse",
    "RecommendationReason",
    "ResourceSummary",
    "ProjectSummary",
    "RecommendationItem",
    "RecommendationListResponse",
    "RecommendationDetailResponse",
    "FeedbackCreateRequest",
    "FeedbackResponse",
    "RoadmapGenerateRequest",
    "RoadmapResponse",
    "RoadmapItemResponse",
    "RoadmapSummaryResponse",
    "SkillSummary",
    "AssessmentQuestionPublic",
    "AssessmentSummary",
    "AssessmentDetailResponse",
    "AnswerSubmissionItem",
    "AssessmentSubmissionRequest",
    "AssessmentResultResponse",
    "AssessmentHistoryItem",
    "AdaptiveIntervention",
    "NextBestActionResponse",
    "AdaptiveEvaluationRequest",
    "AdaptiveEvaluationResponse",
    "GoalAnalysisRequest",
    "LLMGoalExtractionCandidate",
    "ExtractedSkillItem",
    "SuggestedRoleItem",
    "GoalAnalysisData",
    "RetrievedResourceSource",
    "RAGQueryRequest",
    "RAGAnswerResponse",
    "AssistantChatRequest",
    "AssistantMessageItem",
    "AssistantChatData",
    "ConversationSummary",
    "ConversationDetailData",
]
