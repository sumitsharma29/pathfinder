import {
  APIResponse,
  AuthData,
  User,
  LearnerProfile,
  LearnerSkill,
  Role,
  Skill,
  GoalAnalysisData,
  SkillGapAnalysisData,
  RoadmapResponse,
  RoadmapSummaryResponse,
  RoadmapItem,
  OverallProgressResponse,
  SkillProgressItem,
  MilestoneProgressItem,
  NextBestActionResponse,
  RecommendationItem,
  AssessmentSummaryItem,
  AssessmentDetail,
  AssessmentResultResponse,
  AssessmentHistoryItem,
  AdaptiveEvaluationResponse,
  AssistantChatData,
  ConversationSummary,
  ConversationDetailData,
  PaginatedResourcesResponse,
  ResourceCatalogItem,
} from '../types/api';

const envApiUrl = (import.meta.env.VITE_API_URL as string | undefined) || '';
const API_BASE = envApiUrl ? `${envApiUrl.replace(/\/$/, '')}/api/v1` : '/api/v1';

class APIClient {
  private getToken(): string | null {
    return localStorage.getItem('pathfinder_token');
  }

  private setToken(token: string) {
    localStorage.setItem('pathfinder_token', token);
  }

  private clearToken() {
    localStorage.removeItem('pathfinder_token');
    localStorage.removeItem('pathfinder_user');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register') && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }

    let json: any;
    const rawText = await response.text();
    try {
      json = rawText ? JSON.parse(rawText) : {};
    } catch {
      if (!response.ok) {
        const err = new Error(`Server error (${response.status}): ${response.statusText || 'Unable to connect to backend'}`) as any;
        err.status = response.status;
        throw err;
      }
      json = {};
    }

    if (!response.ok || (json.success !== undefined && !json.success)) {
      const errorMessage = json?.error?.message || json?.message || `Request failed with status ${response.status}`;
      const err = new Error(errorMessage) as any;
      err.status = response.status;
      err.details = json?.error?.details || json;
      throw err;
    }

    return json.data !== undefined ? json.data : json;
  }

  // --- Auth Endpoints ---
  async register(name: string, email: string, password: string): Promise<AuthData> {
    const res = await this.request<AuthData>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
    if (res.access_token) {
      this.setToken(res.access_token);
      localStorage.setItem('pathfinder_user', JSON.stringify(res.user));
    }
    return res;
  }

  async login(email: string, password: string): Promise<AuthData> {
    const res = await this.request<AuthData>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (res.access_token) {
      this.setToken(res.access_token);
      localStorage.setItem('pathfinder_user', JSON.stringify(res.user));
    }
    return res;
  }

  async logout(): Promise<void> {
    try {
      await this.request<void>('/auth/logout', { method: 'POST' });
    } finally {
      this.clearToken();
    }
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // --- Profile & Skills ---
  async getProfile(): Promise<LearnerProfile> {
    return this.request<LearnerProfile>('/profile');
  }

  async updateProfile(data: {
    target_role_id?: string;
    experience_level?: string;
    daily_study_hours?: number;
    target_duration_weeks?: number;
    learning_preferences?: Record<string, any>;
  }): Promise<LearnerProfile> {
    return this.request<LearnerProfile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getLearnerSkills(): Promise<LearnerSkill[]> {
    return this.request<LearnerSkill[]>('/profile/skills');
  }

  async addLearnerSkill(skill_id: string, proficiency: number): Promise<LearnerSkill> {
    return this.request<LearnerSkill>('/profile/skills', {
      method: 'POST',
      body: JSON.stringify({ skill_id, proficiency }),
    });
  }

  async updateLearnerSkill(skill_id: string, proficiency: number): Promise<LearnerSkill> {
    return this.request<LearnerSkill>(`/profile/skills/${skill_id}`, {
      method: 'PUT',
      body: JSON.stringify({ proficiency }),
    });
  }

  async deleteLearnerSkill(skill_id: string): Promise<void> {
    return this.request<void>(`/profile/skills/${skill_id}`, {
      method: 'DELETE',
    });
  }

  // --- Catalogs ---
  async getRoles(): Promise<Role[]> {
    return this.request<Role[]>('/roles');
  }

  async getRole(role_id: string): Promise<Role> {
    return this.request<Role>(`/roles/${role_id}`);
  }

  async getSkills(category?: string): Promise<Skill[]> {
    const query = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request<Skill[]>(`/skills${query}`);
  }

  async getSkill(skill_id: string): Promise<Skill> {
    return this.request<Skill>(`/skills/${skill_id}`);
  }

  // --- AI Goal Understanding ---
  async analyzeGoal(raw_text: string): Promise<GoalAnalysisData> {
    return this.request<GoalAnalysisData>('/ai/analyze-goal', {
      method: 'POST',
      body: JSON.stringify({ text: raw_text, goal_text: raw_text }),
    });
  }

  // --- Skill Gaps ---
  async getSkillGaps(): Promise<SkillGapAnalysisData> {
    return this.request<SkillGapAnalysisData>('/skill-gaps');
  }

  async analyzeSkillGaps(role_id?: string): Promise<SkillGapAnalysisData> {
    return this.request<SkillGapAnalysisData>('/skill-gaps/analyze', {
      method: 'POST',
      body: JSON.stringify({ role_id }),
    });
  }

  // --- Roadmaps ---
  async generateRoadmap(target_role_id?: string, target_duration_weeks?: number): Promise<RoadmapResponse> {
    return this.request<RoadmapResponse>('/roadmaps/generate', {
      method: 'POST',
      body: JSON.stringify({ target_role_id, target_duration_weeks }),
    });
  }

  async getCurrentRoadmap(): Promise<RoadmapSummaryResponse> {
    return this.request<RoadmapSummaryResponse>('/roadmaps/current');
  }

  async getRoadmap(roadmap_id: string): Promise<RoadmapResponse> {
    return this.request<RoadmapResponse>(`/roadmaps/${roadmap_id}`);
  }

  async startRoadmapItem(item_id: string): Promise<RoadmapItem> {
    return this.request<RoadmapItem>(`/roadmaps/items/${item_id}/start`, {
      method: 'POST',
    });
  }

  async completeRoadmapItem(item_id: string): Promise<RoadmapItem> {
    return this.request<RoadmapItem>(`/roadmaps/items/${item_id}/complete`, {
      method: 'POST',
    });
  }

  async recalculateRoadmap(roadmap_id: string): Promise<RoadmapResponse> {
    return this.request<RoadmapResponse>(`/roadmaps/${roadmap_id}/recalculate`, {
      method: 'POST',
    });
  }

  // --- Progress ---
  async getOverallProgress(): Promise<OverallProgressResponse> {
    return this.request<OverallProgressResponse>('/progress');
  }

  async getSkillProgress(): Promise<SkillProgressItem[]> {
    return this.request<SkillProgressItem[]>('/progress/skills');
  }

  async getMilestoneProgress(): Promise<MilestoneProgressItem[]> {
    return this.request<MilestoneProgressItem[]>('/progress/milestones');
  }

  async getNextBestAction(): Promise<NextBestActionResponse | null> {
    return this.request<NextBestActionResponse | null>('/progress/next-action');
  }

  // --- Recommendations & Feedback ---
  async getRecommendations(params?: {
    skill_id?: string;
    resource_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<RecommendationItem[]> {
    const q = new URLSearchParams();
    if (params?.skill_id) q.set('skill_id', params.skill_id);
    if (params?.resource_type) q.set('resource_type', params.resource_type);
    if (params?.page) q.set('page', params.page.toString());
    if (params?.page_size) q.set('page_size', params.page_size.toString());
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<RecommendationItem[]>(`/recommendations${qs}`);
  }

  async submitRecommendationFeedback(
    recommendation_id: string,
    feedback: {
      feedback_type: 'helpful' | 'not_helpful' | 'rating' | 'comment';
      rating?: number;
      comment?: string;
    }
  ): Promise<any> {
    return this.request(`/recommendations/${recommendation_id}/feedback`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // --- Assessments ---
  async getAssessments(skill_id?: string): Promise<AssessmentSummaryItem[]> {
    const q = skill_id ? `?skill_id=${encodeURIComponent(skill_id)}` : '';
    return this.request<AssessmentSummaryItem[]>(`/assessments${q}`);
  }

  async getAssessment(assessment_id: string): Promise<AssessmentDetail> {
    return this.request<AssessmentDetail>(`/assessments/${assessment_id}`);
  }

  async submitAssessment(
    assessment_id: string,
    answers: Array<{ question_id: string; answer: string }>
  ): Promise<AssessmentResultResponse> {
    return this.request<AssessmentResultResponse>(`/assessments/${assessment_id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  }

  async getAssessmentResults(assessment_id?: string): Promise<AssessmentHistoryItem[]> {
    const q = assessment_id ? `?assessment_id=${encodeURIComponent(assessment_id)}` : '';
    return this.request<AssessmentHistoryItem[]>(`/assessments/results${q}`);
  }

  // --- Adaptive Engine ---
  async evaluateAdaptation(trigger_event: string = 'MANUAL_EVALUATION', context: Record<string, any> = {}): Promise<AdaptiveEvaluationResponse> {
    return this.request<AdaptiveEvaluationResponse>('/adaptation/evaluate', {
      method: 'POST',
      body: JSON.stringify({ trigger_event, context }),
    });
  }

  // --- Assistant & RAG ---
  async sendAssistantMessage(message: string, conversation_id?: string): Promise<AssistantChatData> {
    return this.request<AssistantChatData>('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id }),
    });
  }

  async getConversations(page: number = 1, page_size: number = 20): Promise<ConversationSummary[]> {
    return this.request<ConversationSummary[]>(`/assistant/conversations?page=${page}&page_size=${page_size}`);
  }

  async getConversation(conversation_id: string): Promise<ConversationDetailData> {
    return this.request<ConversationDetailData>(`/assistant/conversations/${conversation_id}`);
  }

  // --- Resources Catalog ---
  async getResources(params?: {
    page?: number;
    page_size?: number;
    skill_id?: string;
    difficulty?: string;
    resource_type?: string;
    q?: string;
  }): Promise<PaginatedResourcesResponse> {
    const sp = new URLSearchParams();
    if (params?.page) sp.set('page', params.page.toString());
    if (params?.page_size) sp.set('page_size', params.page_size.toString());
    if (params?.skill_id) sp.set('skill_id', params.skill_id);
    if (params?.difficulty) sp.set('difficulty', params.difficulty);
    if (params?.resource_type) sp.set('resource_type', params.resource_type);
    if (params?.q) sp.set('q', params.q);
    const qs = sp.toString() ? `?${sp.toString()}` : '';
    return this.request<PaginatedResourcesResponse>(`/resources${qs}`);
  }

  async getResource(id: string): Promise<ResourceCatalogItem> {
    return this.request<ResourceCatalogItem>(`/resources/${id}`);
  }
}

export const api = new APIClient();
