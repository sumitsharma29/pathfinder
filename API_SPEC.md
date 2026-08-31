# PathFinder AI — API Specification

Document: API_SPEC.md
Version: 1.0
Status: Implementation Specification
Project: PathFinder AI

==================================================
1. PURPOSE
==================================================

This document defines the REST API contract for PathFinder AI.

The backend must use:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- pgvector

The API must expose the application through versioned REST endpoints.

Architecture:

Frontend
    ↓
FastAPI API
    ↓
Service Layer
    ↓
Domain Logic
    ↓
Repository Layer
    ↓
PostgreSQL / pgvector

API routes must NOT contain the complete business logic.

Routes should delegate to services.

==================================================
2. API BASE URL
==================================================

Development:

http://localhost:8000

API:

/api/v1/

Example:

http://localhost:8000/api/v1/profile

Health:

/health

API documentation:

/docs

FastAPI's generated OpenAPI documentation must remain usable.


==================================================
3. API VERSIONING
==================================================

All application APIs must use:

/api/v1/

Do not create unversioned application endpoints such as:

/profile
/roadmap
/recommendations

Correct:

/api/v1/profile
/api/v1/roadmaps
/api/v1/recommendations

This allows future API versions without breaking existing clients.


==================================================
4. API DESIGN PRINCIPLES
==================================================

Every API must:

1. Validate input.
2. Authenticate protected requests.
3. Authorize resource access.
4. Return consistent response structures.
5. Use appropriate HTTP status codes.
6. Avoid exposing internal errors.
7. Use pagination for potentially large collections.
8. Use predictable naming.
9. Return typed response schemas.
10. Never expose sensitive database fields.


==================================================
5. AUTHENTICATION
==================================================

Authentication must be implemented using secure session/token handling.

Passwords must NEVER be stored in plain text.

Use:

Argon2id

or another secure password hashing implementation.

Never store:

- plain passwords
- API keys
- JWT secrets
- database passwords
- private tokens

in source code.

Environment variables must be used.

Required configuration:

DATABASE_URL=
JWT_SECRET=
LLM_API_KEY=
EMBEDDING_API_KEY=
CORS_ORIGINS=
ENVIRONMENT=


==================================================
6. AUTH API
==================================================

POST /api/v1/auth/register

Purpose:

Create a new user account.

Authentication:

Public

Request:

{
  "name": "Sumit Sharma",
  "email": "sumit@example.com",
  "password": "secure-password"
}

Validation:

- name required
- valid email required
- password required
- email must be unique

Success:

HTTP 201

Response:

{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Sumit Sharma",
      "email": "sumit@example.com"
    },
    "access_token": "token"
  },
  "message": "Account created successfully"
}


--------------------------------------------

POST /api/v1/auth/login

Purpose:

Authenticate an existing user.

Authentication:

Public

Request:

{
  "email": "sumit@example.com",
  "password": "secure-password"
}

Success:

HTTP 200

Response:

{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Sumit Sharma",
      "email": "sumit@example.com"
    },
    "access_token": "token"
  },
  "message": "Login successful"
}

Invalid credentials:

HTTP 401


--------------------------------------------

POST /api/v1/auth/logout

Purpose:

Logout current user.

Authentication:

Required

Success:

HTTP 204


--------------------------------------------

GET /api/v1/auth/me

Purpose:

Return authenticated user.

Authentication:

Required

Response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Sumit Sharma",
    "email": "sumit@example.com"
  },
  "message": "Authenticated user"
}


==================================================
7. PROFILE API
==================================================

GET /api/v1/profile

Purpose:

Return current learner profile.

Authentication:

Required

Response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "target_role": {
      "id": "uuid",
      "name": "AI/ML Engineer"
    },
    "experience_level": "beginner",
    "daily_study_hours": 2,
    "target_duration_weeks": 24,
    "learning_preferences": {}
  },
  "message": "Profile retrieved successfully"
}


--------------------------------------------

PUT /api/v1/profile

Purpose:

Create/update learner profile.

Authentication:

Required

Request:

{
  "target_role_id": "uuid",
  "experience_level": "beginner",
  "daily_study_hours": 2,
  "target_duration_weeks": 24,
  "learning_preferences": {
    "content_types": [
      "video",
      "project"
    ]
  }
}

Validation:

daily_study_hours >= 0

target_duration_weeks > 0

Success:

HTTP 200


--------------------------------------------

GET /api/v1/profile/skills

Purpose:

Return learner's current skills.

Authentication:

Required

Response:

{
  "success": true,
  "data": [
    {
      "skill_id": "uuid",
      "skill_name": "Python",
      "proficiency": 70,
      "source": "self_declared",
      "confidence": 0.8
    }
  ],
  "message": "Skills retrieved successfully"
}


--------------------------------------------

POST /api/v1/profile/skills

Purpose:

Add a learner skill.

Authentication:

Required

Request:

{
  "skill_id": "uuid",
  "proficiency": 70,
  "source": "self_declared",
  "confidence": 0.8
}

Validation:

proficiency:

0 <= proficiency <= 100

confidence:

0 <= confidence <= 1

Success:

HTTP 201


--------------------------------------------

PUT /api/v1/profile/skills/{skill_id}

Purpose:

Update learner skill proficiency.

Authentication:

Required

Request:

{
  "proficiency": 75,
  "source": "assessment",
  "confidence": 0.95
}

Success:

HTTP 200


--------------------------------------------

DELETE /api/v1/profile/skills/{skill_id}

Purpose:

Remove a learner skill.

Authentication:

Required

Success:

HTTP 204

If skill does not exist:

404


==================================================
8. GOAL ANALYSIS API
==================================================

POST /api/v1/ai/analyze-goal

Purpose:

Analyze a natural-language career goal.

Authentication:

Required

Request:

{
  "text": "I want to become a data scientist in six months"
}

AI output must be structured.

Expected response structure:

{
  "target_role": "Data Scientist",
  "timeline_weeks": 24,
  "confidence": 0.94,
  "missing_information": []
}

The service may additionally return:

{
  "technologies": [],
  "experience_level": null,
  "daily_study_hours": null,
  "existing_skills": [],
  "preferences": {}
}

Important:

If information is ambiguous, return null.

Do NOT invent missing information.

Success:

HTTP 200

AI failure:

503

Error code:

GOAL_ANALYSIS_FAILED

The AI output must be validated using Pydantic before being used by business logic.


==================================================
9. SKILL GAP API
==================================================

POST /api/v1/skill-gaps/analyze

Purpose:

Calculate the learner's current skill gaps against the target role.

Authentication:

Required

Processing:

Learner Profile
    ↓
Target Role
    ↓
Required Skills
    ↓
Learner Skills
    ↓
Skill Gap
    ↓
Priority

Skill gap:

gap =
required_proficiency - learner_proficiency

Minimum gap:

0

Example:

Required = 80
Current = 35

Gap = 45


Response:

{
  "success": true,
  "data": {
    "target_role": "AI/ML Engineer",
    "skills": [
      {
        "skill_id": "uuid",
        "skill": "Statistics",
        "required": 80,
        "current": 35,
        "gap": 45,
        "importance": 0.9,
        "priority": 0.82
      }
    ]
  },
  "message": "Skill gap analysis completed"
}


--------------------------------------------

GET /api/v1/skill-gaps

Purpose:

Return previously calculated/current skill gaps.

Authentication:

Required

Supports pagination where appropriate.

Query parameters:

?page=1&page_size=20


==================================================
10. ROADMAP API
==================================================

POST /api/v1/roadmaps/generate

Purpose:

Generate a new learner roadmap.

Authentication:

Required

Request:

{
  "target_role_id": "uuid",
  "target_duration_weeks": 24
}

If the learner profile already contains these values, they may be used as defaults.

Pipeline:

Learner Profile
    ↓
Target Role
    ↓
Required Skills
    ↓
Skill Gaps
    ↓
Missing Prerequisites
    ↓
Candidate Resources
    ↓
Eligibility Filtering
    ↓
Scoring
    ↓
Semantic Ranking
    ↓
Diversity Filtering
    ↓
Roadmap Generation
    ↓
Explanation

The roadmap MUST be prerequisite-aware.

Do not simply sort by largest skill gap.

Example:

Machine Learning
    ↓
Deep Learning

Deep Learning must not appear before Machine Learning if the prerequisite is not satisfied.

Success:

HTTP 201

Response:

{
  "success": true,
  "data": {
    "roadmap_id": "uuid",
    "version": 1,
    "status": "active",
    "estimated_weeks": 24,
    "items": []
  },
  "message": "Roadmap generated successfully"
}

Failure:

503 or 500 depending on cause.

Error:

ROADMAP_GENERATION_FAILED


--------------------------------------------

GET /api/v1/roadmaps/current

Purpose:

Return the learner's active roadmap.

Authentication:

Required

Response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "version": 2,
    "status": "active",
    "estimated_weeks": 24,
    "items": []
  },
  "message": "Current roadmap retrieved successfully"
}


--------------------------------------------

GET /api/v1/roadmaps/{id}

Purpose:

Return a specific roadmap.

Authentication:

Required

Authorization:

The roadmap must belong to the authenticated learner.

If another learner attempts access:

403


--------------------------------------------

POST /api/v1/roadmaps/{id}/recalculate

Purpose:

Recalculate an existing roadmap after learner state changes.

Possible triggers:

- assessment result
- profile change
- study time change
- goal change
- feedback
- adaptive update

The system should create a new version where a major roadmap change occurs.

Do not destroy useful historical roadmap state.

Success:

HTTP 200


==================================================
11. ROADMAP ITEM API
==================================================

GET /api/v1/roadmaps/items/{id}

Purpose:

Return roadmap item details.

Authentication:

Required

Authorization:

Item must belong to authenticated learner.

Response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "sequence": 1,
    "skill": {},
    "resource": {},
    "project": null,
    "assessment": null,
    "status": "AVAILABLE",
    "progress": 0,
    "estimated_hours": 4,
    "reason": {}
  },
  "message": "Roadmap item retrieved successfully"
}


--------------------------------------------

POST /api/v1/roadmaps/items/{id}/start

Purpose:

Start an available roadmap item.

Authentication:

Required

Allowed transition:

AVAILABLE → IN_PROGRESS

If item is LOCKED:

Return:

HTTP 403

Error:

PREREQUISITE_NOT_MET

If invalid transition:

HTTP 409


--------------------------------------------

POST /api/v1/roadmaps/items/{id}/complete

Purpose:

Complete a roadmap item.

Authentication:

Required

Allowed transition:

IN_PROGRESS → COMPLETED

Completion should update actual progress data.

Do not simply update a disconnected dashboard number.

Success:

HTTP 200


==================================================
12. RECOMMENDATION API
==================================================

GET /api/v1/recommendations

Purpose:

Return personalized learning recommendations.

Authentication:

Required

Query parameters:

?page=1
&page_size=20
&skill_id=uuid
&resource_type=course

Recommendations must use the hybrid recommendation pipeline.

Candidate filtering should consider:

- active resource
- required skills
- learner level
- prerequisite availability
- resource difficulty
- target role relevance
- estimated duration

Recommendation scoring:

Score =
0.30 × SkillGapRelevance
+
0.20 × PrerequisiteFit
+
0.15 × GoalRelevance
+
0.15 × DifficultyFit
+
0.10 × TimeFit
+
0.10 × PreferenceFit

All values must be normalized.

Weights must remain configurable.


--------------------------------------------

GET /api/v1/recommendations/{id}

Purpose:

Return one recommendation and its explanation.

Response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "resource": {},
    "score": 0.91,
    "ranking": 1,
    "reason": {
      "skill_gap": 0.68,
      "goal_relevance": 0.92,
      "prerequisite_fit": 1.0,
      "difficulty_fit": 0.88,
      "time_fit": 0.91
    },
    "algorithm_version": "v1"
  },
  "message": "Recommendation retrieved successfully"
}


--------------------------------------------

POST /api/v1/recommendations/{id}/feedback

Purpose:

Submit learner feedback on a recommendation.

Authentication:

Required

Request:

{
  "feedback_type": "helpful",
  "rating": 5,
  "comment": "Very useful resource"
}

Success:

HTTP 201


==================================================
13. ASSESSMENT API
==================================================

GET /api/v1/assessments

Purpose:

Return available assessments.

Authentication:

Required

Query:

?page=1&page_size=20
&skill_id=uuid


--------------------------------------------

GET /api/v1/assessments/{id}

Purpose:

Return assessment questions.

Authentication:

Required

CRITICAL:

Never return:

correct_answer

to the frontend.

Question response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Machine Learning Fundamentals",
    "skill": {
      "id": "uuid",
      "name": "Machine Learning"
    },
    "questions": [
      {
        "id": "uuid",
        "question": "What is overfitting?",
        "question_type": "multiple_choice",
        "options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "points": 2
      }
    ]
  },
  "message": "Assessment retrieved successfully"
}


--------------------------------------------

POST /api/v1/assessments/{id}/submit

Purpose:

Submit assessment answers.

Authentication:

Required

Request:

{
  "answers": [
    {
      "question_id": "uuid",
      "answer": "Option A"
    }
  ]
}

Backend processing:

Submit Assessment
    ↓
Validate answers
    ↓
Calculate score
    ↓
Calculate skill mastery
    ↓
Save assessment result
    ↓
Update learner skill state
    ↓
Detect weak skills
    ↓
Trigger adaptive engine
    ↓
Update roadmap if required

This operation must use a transaction where atomicity is required.

Success:

HTTP 200

Response:

{
  "success": true,
  "data": {
    "assessment_id": "uuid",
    "score": 78,
    "skill_mastery": 78,
    "passed": true,
    "attempt_number": 1,
    "adaptive_update": {
      "roadmap_updated": true
    }
  },
  "message": "Assessment submitted successfully"
}

Already submitted error:

409

Code:

ASSESSMENT_ALREADY_SUBMITTED


--------------------------------------------

GET /api/v1/assessments/results

Purpose:

Return learner assessment history.

Authentication:

Required

Query:

?page=1&page_size=20
&assessment_id=uuid

Return:

- assessment
- score
- mastery
- attempt number
- created_at

Do not expose correct answers.


==================================================
14. PROGRESS API
==================================================

GET /api/v1/progress

Purpose:

Return overall learner progress.

Authentication:

Required

Progress must be derived from actual learner activity.

Possible response:

{
  "success": true,
  "data": {
    "overall_percentage": 42,
    "completed_items": 8,
    "total_items": 20,
    "time_spent_minutes": 740,
    "current_milestone": {}
  },
  "message": "Progress retrieved successfully"
}

Do not return arbitrary hardcoded dashboard numbers.


--------------------------------------------

GET /api/v1/progress/skills

Purpose:

Return skill-level progress.

Response:

{
  "success": true,
  "data": [
    {
      "skill_id": "uuid",
      "skill": "Python",
      "current_proficiency": 72,
      "required_proficiency": 85,
      "gap": 13
    }
  ],
  "message": "Skill progress retrieved successfully"
}


--------------------------------------------

GET /api/v1/progress/milestones

Purpose:

Return roadmap milestone progress.

Response:

{
  "success": true,
  "data": [
    {
      "roadmap_item_id": "uuid",
      "title": "Python Fundamentals",
      "status": "COMPLETED",
      "percentage": 100
    }
  ],
  "message": "Milestone progress retrieved successfully"
}


--------------------------------------------

GET /api/v1/progress/next-action

Purpose:

Return the next best action for the learner.

The engine must consider:

- current roadmap state
- unlocked items
- weak skills
- pending assessments
- user availability
- priority

Priority order:

1. Required intervention
2. Current milestone
3. Pending assessment
4. High-priority skill
5. Optional enrichment

Never recommend a LOCKED item.


==================================================
15. AI ASSISTANT API
==================================================

POST /api/v1/assistant/chat

Purpose:

Send a message to PathFinder AI Assistant.

Authentication:

Required

Request:

{
  "conversation_id": "uuid",
  "message": "What should I study today?"
}

conversation_id may be null for a new conversation.

Backend should dynamically build relevant context.

Example context:

Learner:
AI/ML Engineer

Current Skills:
Python 70%
SQL 55%

Current Milestone:
Machine Learning

Weak Skills:
Statistics
Model Evaluation

Study Time:
2 hours/day

Current Recommendation:
Model Evaluation Refresher

Do NOT send the entire database to the LLM.

Response:

{
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "message": {
      "id": "uuid",
      "role": "assistant",
      "content": "Your best next step is..."
    },
    "sources": []
  },
  "message": "Assistant response generated successfully"
}

AI responses must be grounded in:

- learner profile
- application database
- retrieved resources

The assistant must not invent resource facts.


--------------------------------------------

GET /api/v1/assistant/conversations

Purpose:

Return learner's conversations.

Authentication:

Required

Pagination required.

Example:

?page=1&page_size=20


--------------------------------------------

GET /api/v1/assistant/conversations/{id}

Purpose:

Return one conversation and its messages.

Authentication:

Required

Authorization:

Conversation must belong to authenticated learner.

Never allow one learner to access another learner's conversation.


==================================================
16. RESOURCES API
==================================================

The core technical specification defines resource relationships and resource detail requirements.

Recommended public application endpoints:

GET /api/v1/resources

GET /api/v1/resources/{id}

These endpoints should return only active resources.

Supported filters:

?page=1
&page_size=20
&skill_id=uuid
&difficulty=beginner
&resource_type=course
&provider=...

Resource response:

{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Machine Learning Course",
    "description": "...",
    "resource_type": "course",
    "provider": "...",
    "url": "...",
    "difficulty": "intermediate",
    "estimated_minutes": 600,
    "quality_score": 92,
    "skills": []
  },
  "message": "Resource retrieved successfully"
}

Do not return internal embedding vectors.


==================================================
17. SKILLS API
==================================================

Recommended reference-data endpoints:

GET /api/v1/skills

GET /api/v1/skills/{id}

GET /api/v1/roles

GET /api/v1/roles/{id}

These are primarily used by:

- onboarding
- profile
- skill selection
- roadmap generation
- filtering
- frontend dropdowns

Pagination should be used for large collections.


==================================================
18. RESPONSE FORMAT
==================================================

All successful API responses must follow:

{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}

Example:

{
  "success": true,
  "data": {
    "id": "uuid"
  },
  "message": "Profile retrieved successfully"
}


All errors must follow:

{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found"
  }
}

Never expose stack traces.

Never expose:

- SQL errors
- Python stack traces
- internal paths
- API keys
- database credentials
- LLM provider secrets


==================================================
19. HTTP STATUS CODES
==================================================

Use:

200 OK

201 Created

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error

503 Service Unavailable


==================================================
20. ERROR TAXONOMY
==================================================

Use application-level error codes.

Required codes include:

AUTH_INVALID_CREDENTIALS
AUTH_UNAUTHORIZED
PROFILE_INCOMPLETE
GOAL_ANALYSIS_FAILED
SKILL_NOT_FOUND
ROADMAP_GENERATION_FAILED
PREREQUISITE_NOT_MET
ASSESSMENT_NOT_FOUND
ASSESSMENT_ALREADY_SUBMITTED
RESOURCE_UNAVAILABLE
AI_SERVICE_UNAVAILABLE
RATE_LIMIT_EXCEEDED

Additional useful codes:

PROFILE_NOT_FOUND
ROADMAP_NOT_FOUND
ROADMAP_ITEM_NOT_FOUND
RECOMMENDATION_NOT_FOUND
CONVERSATION_NOT_FOUND
FORBIDDEN_RESOURCE_ACCESS
INVALID_STATE_TRANSITION
VALIDATION_ERROR
INTERNAL_SERVER_ERROR


==================================================
21. AUTHORIZATION RULES
==================================================

Every protected endpoint must identify the current learner from the authenticated session/token.

Never trust:

learner_id

sent by the frontend.

Example:

BAD:

POST /api/v1/progress

{
  "learner_id": "someone-else"
}

The backend must derive the learner identity from authentication.

A learner may access only their own:

- profile
- skills
- roadmap
- progress
- recommendations
- assessment results
- feedback
- conversations

Reference data may be shared according to application permissions.


==================================================
22. PAGINATION
==================================================

Potentially large collections must support pagination.

Default:

page = 1

page_size = 20

Maximum:

page_size = 100

Recommended response:

{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "message": "Data retrieved successfully"
}


==================================================
23. INPUT VALIDATION
==================================================

Use Pydantic request schemas.

Examples:

Proficiency:

0–100

Confidence:

0–1

Rating:

1–5

Percentage:

0–100

Study hours:

>= 0

Timeline:

> 0

Page:

>= 1

Page size:

1–100

Invalid input must return:

HTTP 422


==================================================
24. AI OUTPUT VALIDATION
==================================================

Whenever AI output is used by backend logic:

AI
 ↓
Structured Output
 ↓
Pydantic Validation
 ↓
Business Logic

If validation fails:

1. Retry if appropriate.
2. Attempt controlled repair if safe.
3. Fallback.
4. Return clear error.

Never blindly trust malformed LLM output.


==================================================
25. AI FAILURE HANDLING
==================================================

LLM failure:

LLM failure
    ↓
Retry if appropriate
    ↓
Fallback
    ↓
User-friendly error

Goal analysis may fall back to a manual structured form.

Recommendations must retain deterministic recommendation logic even when the LLM is unavailable.

The system must NOT become unusable just because the LLM fails.


==================================================
26. AI COST CONTROL
==================================================

Do NOT call the LLM for deterministic operations.

Avoid LLM calls for:

- progress percentages
- arithmetic
- prerequisite checks
- database lookups
- deterministic ranking calculations

Use AI only where it provides meaningful value.


==================================================
27. RAG API BEHAVIOR
==================================================

RAG pipeline:

User Question
    ↓
Context Builder
    ↓
Query Construction
    ↓
Vector Retrieval
    ↓
Metadata Filtering
    ↓
Top-K Results
    ↓
Context Assembly
    ↓
LLM
    ↓
Response Validation
    ↓
User

When answering questions about a resource, responses must be grounded in retrieved resource data.

Do not allow unsupported resource claims.


==================================================
28. SERVICE MAPPING
==================================================

API routers should delegate to services.

Auth:

AuthRouter
    ↓
AuthService

Profile:

ProfileRouter
    ↓
LearnerProfileService

Skill Gap:

SkillGapRouter
    ↓
SkillGapService

Recommendations:

RecommendationRouter
    ↓
RecommendationService

Roadmap:

RoadmapRouter
    ↓
RoadmapService

Assessment:

AssessmentRouter
    ↓
AssessmentService

Progress:

ProgressRouter
    ↓
ProgressService

Assistant:

AssistantRouter
    ↓
AssistantService


==================================================
29. BACKEND FILE ORGANIZATION
==================================================

Recommended:

backend/app/api/

auth.py
profile.py
skills.py
roadmap.py
recommendations.py
assessments.py
progress.py
assistant.py
resources.py
roles.py
skill_gaps.py

Schemas:

backend/app/schemas/

auth.py
profile.py
skill.py
role.py
resource.py
roadmap.py
recommendation.py
assessment.py
progress.py
assistant.py
common.py
errors.py

Services:

backend/app/services/

auth_service.py
learner_profile_service.py
skill_service.py
skill_gap_service.py
recommendation_service.py
roadmap_service.py
assessment_service.py
progress_service.py
feedback_service.py
adaptive_learning_service.py
assistant_service.py
ai_service.py
rag_service.py

Repositories:

backend/app/repositories/

user_repository.py
learner_profile_repository.py
skill_repository.py
role_repository.py
resource_repository.py
roadmap_repository.py
assessment_repository.py
progress_repository.py
recommendation_repository.py
conversation_repository.py


==================================================
30. ROUTER RULE
==================================================

A route handler should remain thin.

Example:

POST /api/v1/roadmaps/generate

Router
    ↓
Validate request
    ↓
Authenticate learner
    ↓
RoadmapService.generate()
    ↓
Return response

Do NOT implement:

skill gap algorithm
prerequisite traversal
recommendation scoring
database queries
LLM prompts

directly inside the route handler.


==================================================
31. ROADMAP GENERATION SAFETY
==================================================

Simultaneous roadmap generation requests must not create duplicate active roadmaps.

Use:

- idempotency
- locking where necessary
- status checks
- transactions

Only the appropriate roadmap version should be active.


==================================================
32. ASSESSMENT TRANSACTION
==================================================

Assessment submission must be treated as an atomic operation.

Flow:

Submit Assessment
    ↓
Validate submission
    ↓
Calculate score
    ↓
Save result
    ↓
Update learner skill mastery
    ↓
Detect weak skills
    ↓
Trigger adaptive learning
    ↓
Update roadmap/version if required

If an atomic operation fails, prevent partial inconsistent state.


==================================================
33. NEXT BEST ACTION
==================================================

GET:

/api/v1/progress/next-action

The service must consider:

Current roadmap state
+
Unlocked items
+
Weak skills
+
Pending assessments
+
User availability
+
Priority

Priority:

1. Required intervention
2. Current milestone
3. Pending assessment
4. High-priority skill
5. Optional enrichment

Never return a LOCKED roadmap item as the next action.


==================================================
34. RESOURCE SECURITY
==================================================

Resource URLs must come from database records.

Do not allow AI-generated URLs to be treated as trusted resources.

Resource ingestion must validate:

- required fields
- URL format
- duplicate records
- skill references

Only active resources should be recommended.


==================================================
35. LOGGING
==================================================

Use structured logging.

Log:

- request IDs
- API errors
- important state transitions
- AI operation metadata
- recommendation events

Never log:

- passwords
- API keys
- authentication tokens
- unnecessary sensitive learner content


==================================================
36. API DOCUMENTATION
==================================================

Every important endpoint must include:

- description
- request schema
- response schema
- error responses

FastAPI OpenAPI documentation must be available through:

/docs

and should remain usable throughout development.


==================================================
37. HEALTH API
==================================================

GET /health

Purpose:

Check application availability.

Response:

{
  "status": "ok"
}

Do not expose sensitive infrastructure information.

An advanced implementation may check database/AI connectivity internally.


==================================================
38. API TESTING REQUIREMENTS
==================================================

Test every important endpoint for:

- valid request
- invalid request
- missing authentication
- unauthorized access
- missing resource
- malformed data
- duplicate operations
- database failure
- AI failure
- rate limiting
- invalid state transitions

Important security test:

User A must never be able to access User B's:

- profile
- roadmap
- progress
- assessment results
- recommendations
- conversations


==================================================
39. CRITICAL E2E API FLOW
==================================================

The complete backend flow must support:

Register
    ↓
Login
    ↓
Profile
    ↓
Goal Analysis
    ↓
Skill Gap
    ↓
Roadmap Generation
    ↓
Roadmap Item
    ↓
Start Learning
    ↓
Complete Learning
    ↓
Assessment
    ↓
Assessment Result
    ↓
Skill Mastery Update
    ↓
Adaptive Update
    ↓
Roadmap Version Update
    ↓
Dashboard Progress
    ↓
AI Assistant


==================================================
40. API DEFINITION OF DONE
==================================================

[ ] FastAPI application starts
[ ] /health works
[ ] /docs works
[ ] API uses /api/v1/
[ ] Registration works
[ ] Login works
[ ] Logout works
[ ] /auth/me works
[ ] Authentication is enforced
[ ] Authorization is enforced
[ ] Profile API works
[ ] Learner skills API works
[ ] Goal analysis works
[ ] Goal AI output is validated
[ ] Skill gap analysis works
[ ] Roadmap generation works
[ ] Roadmap retrieval works
[ ] Roadmap recalculation works
[ ] Roadmap item start works
[ ] Roadmap item completion works
[ ] Recommendation API works
[ ] Recommendation feedback works
[ ] Assessment listing works
[ ] Assessment detail works
[ ] Correct answers are never exposed
[ ] Assessment submission works
[ ] Assessment results work
[ ] Adaptive update works
[ ] Progress API works
[ ] Next-best-action works
[ ] AI Assistant works
[ ] Conversations work
[ ] Resources API works
[ ] Skills API works
[ ] Roles API works
[ ] Pagination works
[ ] Consistent response format works
[ ] Error taxonomy implemented
[ ] HTTP status codes are correct
[ ] AI failure fallback works
[ ] RAG grounding works where implemented
[ ] Sensitive information is not exposed
[ ] API tests pass
[ ] E2E flow passes


==================================================
41. FINAL API ARCHITECTURE
==================================================

                     FRONTEND
                         │
                         ▼
                  /api/v1/*
                         │
             ┌───────────┴───────────┐
             │                       │
         AUTH APIs              LEARNER APIs
             │                       │
             │             ┌─────────┼─────────┐
             │             │         │         │
             ▼             ▼         ▼         ▼
          Profile       Skill Gap  Roadmap  Progress
                                      │
                                      ▼
                              Recommendation
                                      │
                                      ▼
                                  Assessment
                                      │
                                      ▼
                              Adaptive Engine
                                      │
                                      ▼
                                  AI/RAG
                                      │
                                      ▼
                           PostgreSQL + pgvector


==================================================
42. IMPORTANT IMPLEMENTATION RULE
==================================================

Do not invent new API behavior that conflicts with:

PROJECT_CONTEXT.md
PRODUCT_REQUIREMENTS.md
TECHNICAL_SPEC.md
DATABASE_SPEC.md

The API is the contract between frontend and backend.

Implement the API contract first.

Then implement:

1. Pydantic schemas
2. Routers
3. Services
4. Repositories
5. Database queries
6. AI integrations
7. Tests

The frontend must consume the API through a centralized API client.

Do not make random raw fetch calls from individual UI components.


==================================================
END OF API_SPEC.md
==================================================