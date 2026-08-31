// Common API Response Envelope
export interface APIResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// User & Auth
export interface User {
  id: string;
  name: string;
  email: string;
}

export interface AuthData {
  user: User;
  access_token: string;
  token_type: string;
}

// Role & Skill
export interface Role {
  id: string;
  name: string;
  slug: string;
  description?: string;
  required_skills?: RoleSkillItem[];
}

export interface RoleSkillItem {
  skill_id: string;
  skill_name: string;
  skill_slug: string;
  category: string;
  importance: number;
  minimum_proficiency: number;
}

export interface Skill {
  id: string;
  name: string;
  slug: string;
  category: string;
  description?: string;
  prerequisites?: SkillPrerequisiteItem[];
}

export interface SkillPrerequisiteItem {
  prerequisite_skill_id: string;
  prerequisite_skill_name: string;
  required_proficiency: number;
}

// Profile
export interface LearnerProfile {
  id: string;
  user_id: string;
  target_role: {
    id: string;
    name: string;
    slug: string;
  } | null;
  experience_level: string;
  daily_study_hours: number | null;
  target_duration_weeks: number | null;
  learning_preferences: Record<string, any>;
}

export interface LearnerSkill {
  id: string;
  skill_id: string;
  skill_name: string;
  skill_slug: string;
  category: string;
  proficiency: number;
  source: string;
  last_assessed_at: string | null;
}

// AI Goal Extraction (Exact mirror of backend/app/schemas/goal.py)
export interface ExtractedSkillItem {
  name: string;
  matched_name?: string | null;
  skill_id?: string | null;
  confidence: number;
  status: string; // CONFIRMED | INFERRED | UNRESOLVED
}

export interface SuggestedRoleItem {
  id: string;
  name: string;
  slug: string;
  match_score: number;
}

export interface GoalAnalysisData {
  raw_goal: string;
  target_role?: string | null;
  role_id?: string | null;
  role_slug?: string | null;
  role_confidence: number;
  timeline_weeks?: number | null;
  daily_study_hours?: number | null;
  experience_level?: string | null;
  known_skills: ExtractedSkillItem[];
  technologies: string[];
  preferences: Record<string, any>;
  confidence: number;
  status: string; // RESOLVED | AMBIGUOUS | UNRESOLVED | CLARIFICATION_REQUIRED
  missing_information: string[];
  clarification_prompt?: string | null;
  suggested_roles: SuggestedRoleItem[];
}

// Dynamic Skill Gaps
export interface SkillGapItem {
  skill_id: string;
  skill: string;
  category: string;
  current: number;
  required: number;
  gap: number;
  importance: number;
  status: 'MASTERED' | 'PARTIAL' | 'MISSING';
}

export interface SkillGapSummary {
  total_skills_required: number;
  skills_mastered: number;
  skills_in_progress: number;
  skills_missing: number;
  average_gap: number;
  overall_readiness_percentage: number;
}

export interface SkillGapAnalysisData {
  target_role_id: string;
  target_role: string;
  summary: SkillGapSummary;
  skills: SkillGapItem[];
}

// Roadmap
export interface RoadmapItemResource {
  id: string;
  title: string;
  url: string;
  resource_type: string;
  provider?: string;
  difficulty?: string;
  estimated_hours?: number;
  quality_score?: number;
  is_free?: boolean;
  skills_covered?: string[];
}

export interface RoadmapItem {
  id: string;
  roadmap_id: string;
  sequence: number;
  skill?: {
    id: string;
    name: string;
    slug: string;
    category: string;
  } | null;
  resource?: RoadmapItemResource | null;
  project?: {
    id: string;
    title: string;
    description: string;
    difficulty: string;
    estimated_hours?: number;
    skills_covered?: string[];
  } | null;
  assessment?: any;
  status: 'LOCKED' | 'AVAILABLE' | 'IN_PROGRESS' | 'COMPLETED';
  progress: number;
  estimated_hours?: number | null;
  reason?: Record<string, any>;
  locked_reason?: string | null;
  created_at?: string;
}

export interface RoadmapSummaryResponse {
  roadmap_id: string;
  version: number;
  status: string;
  estimated_weeks: number;
  total_items: number;
  completed_items: number;
  in_progress_items: number;
  available_items: number;
  locked_items: number;
  overall_progress: number;
  next_best_action?: RoadmapItem | null;
  items: RoadmapItem[];
}

export interface RoadmapResponse {
  id: string;
  learner_id: string;
  role_id: string;
  role_name?: string;
  version: number;
  status: string;
  estimated_weeks: number;
  items: RoadmapItem[];
  created_at?: string;
}

// Progress Tracking
export interface MilestoneSummary {
  roadmap_item_id: string;
  title: string;
  status: string;
  sequence_order: number;
  estimated_minutes: number;
  skill_id: string;
  skill_name: string;
}

export interface OverallProgressResponse {
  overall_percentage: number;
  completed_items: number;
  total_items: number;
  time_spent_minutes: number;
  active_roadmap_id: string | null;
  current_milestone: MilestoneSummary | null;
}

export interface SkillProgressItem {
  skill_id: string;
  skill: string;
  category: string;
  current_proficiency: number;
  required_proficiency: number;
  gap: number;
  status: string;
  importance: number;
}

export interface MilestoneProgressItem {
  roadmap_item_id: string;
  title: string;
  status: string;
  percentage: number;
  sequence_order: number;
  estimated_minutes: number;
  skill_id: string;
  skill_name: string;
  resource_id?: string | null;
  resource_title?: string | null;
}

// Next Best Action
export interface NextBestActionResponse {
  action_type: 'foundational_intervention' | 'study_item' | 'attempt_assessment' | 'reinforce_skill' | 'select_role' | 'generate_roadmap' | 'completed';
  id?: string | null;
  title: string;
  reason: string;
  estimated_hours?: number | null;
  resource_id?: string | null;
  assessment_id?: string | null;
}

// Recommendations
export interface RecommendationItem {
  recommendation_id: string;
  resource_id: string;
  title: string;
  url: string;
  resource_type: string;
  provider?: string;
  difficulty?: string;
  estimated_hours?: number;
  quality_score?: number;
  is_free?: boolean;
  score: number;
  reason: {
    primary_reason: string;
    addressed_skill_name: string;
    gap_addressed: number;
    skill_importance: number;
    quality_boost: number;
    difficulty_match: number;
    prerequisites_met: boolean;
  };
}

// Assessments (Exact mirror of backend/app/schemas/assessment.py)
export interface AssessmentQuestionPublic {
  id: string;
  question: string;
  question_type: string;
  options?: Record<string, any>;
  points: number;
}

export interface AssessmentSummaryItem {
  id: string;
  title: string;
  description?: string;
  difficulty?: string;
  passing_score: number;
  skill?: {
    id: string;
    name: string;
    slug: string;
    category?: string;
  };
  question_count: number;
  created_at: string;
}

export interface AssessmentDetail {
  id: string;
  title: string;
  description?: string;
  difficulty?: string;
  passing_score: number;
  skill?: {
    id: string;
    name: string;
    slug: string;
    category?: string;
  };
  questions: AssessmentQuestionPublic[];
  created_at: string;
}

export interface AnswerSubmissionItem {
  question_id: string;
  answer: string;
}

export interface AssessmentResultResponse {
  id: string;
  assessment_id: string;
  assessment_title: string;
  skill_id: string;
  skill_name: string;
  attempt_number: number;
  score: number;
  skill_mastery: number;
  passed: boolean;
  total_questions: number;
  correct_count: number;
  created_at: string;
}

export interface AssessmentHistoryItem {
  id: string;
  assessment_id: string;
  assessment_title: string;
  skill_name: string;
  attempt_number: number;
  score: number;
  skill_mastery: number;
  passed: boolean;
  created_at: string;
}

// Adaptive Engine
export interface AdaptiveEvaluationResponse {
  learner_id: string;
  trigger_event: string;
  weak_skills_detected: Array<{
    skill_id: string;
    skill_name: string;
    current_proficiency: number;
    required_proficiency: number;
    gap: number;
    reason: string;
  }>;
  interventions_selected: Array<{
    skill_id: string;
    skill_name: string;
    intervention_type: string;
    priority: number;
    suggested_resource_ids: string[];
    explanation: string;
  }>;
  roadmap_updated: boolean;
  roadmap_version?: number;
  next_best_action?: NextBestActionResponse | null;
}

// Assistant & RAG (Exact mirror of backend/app/schemas/assistant.py)
export interface CitationSource {
  resource_id: string;
  title: string;
  description?: string | null;
  url: string;
  resource_type?: string;
  difficulty?: string | null;
  similarity_score?: number;
  matched_skills?: string[];
  provider?: string;
}

export interface AssistantMessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  sources?: CitationSource[];
}

export interface AssistantChatResponse {
  conversation_id: string;
  message: AssistantMessageItem;
  sources: CitationSource[];
}

export type AssistantChatData = AssistantChatResponse;

export interface ConversationSummary {
  id: string;
  title?: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title?: string | null;
  messages: AssistantMessageItem[];
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  created_at: string;
  sources?: CitationSource[];
}

export interface ConversationDetailData {
  id: string;
  title: string;
  created_at: string;
  messages: ConversationMessage[];
}

// Resources Catalog
export interface ResourceCatalogItem {
  id: string;
  title: string;
  description?: string;
  resource_type: string;
  provider?: string;
  url: string;
  difficulty?: string;
  estimated_minutes?: number;
  quality_score?: number;
  is_active: boolean;
  skills?: Array<{ id: string; name: string }>;
}

export interface PaginatedResourcesResponse {
  items: ResourceCatalogItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
