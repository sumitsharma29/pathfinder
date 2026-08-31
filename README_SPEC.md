# PathFinder AI

Your Goal. Your Skills. Your Path.

PathFinder AI is an intelligent personalized learning
navigation platform that converts a learner's career goal,
current skills, skill gaps and learning preferences into
an explainable and adaptive learning roadmap.

==================================================
1. PROJECT OVERVIEW
==================================================

PathFinder follows:

Goal
 ↓
Learner Profile
 ↓
Skill Gap Analysis
 ↓
Skill Dependencies
 ↓
Recommendations
 ↓
Personalized Roadmap
 ↓
Learning
 ↓
Assessment
 ↓
Mastery
 ↓
Adaptive Roadmap
 ↓
Next Best Action


The platform is designed around one core question:

"What should this learner do next, and why?"


==================================================
2. CORE FEATURES
==================================================

P0:

- Authentication
- AI-assisted onboarding
- Natural-language goal understanding
- Learner profile
- Skill management
- Skill gap analysis
- Skill dependency graph
- Personalized recommendations
- Explainable recommendations
- Personalized roadmap
- Resource discovery
- Assessments
- Progress tracking
- Adaptive learning
- Dashboard
- Context-aware AI Assistant
- RAG-based learning assistance


P1:

- Resource feedback
- Project recommendations
- Roadmap history
- Advanced progress visualization
- Mobile polish


P2:

- Resume analysis
- GitHub analysis
- Voice assistant
- Gamification
- Certification recommendations
- Career market intelligence


==================================================
3. TECHNOLOGY STACK
==================================================

Frontend:

React
TypeScript
Vite
Tailwind CSS
Recharts


Backend:

Python
FastAPI
Pydantic
SQLAlchemy
Alembic


Database:

PostgreSQL
pgvector


AI:

LLM provider abstraction
Embedding provider abstraction
RAG


Testing:

pytest
Vitest
React Testing Library
Playwright


==================================================
4. ARCHITECTURE
==================================================

                    FRONTEND
                        │
                        ▼
                    FASTAPI
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
  DOMAIN LOGIC       AI LAYER        RAG LAYER
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                  POSTGRESQL
                    + PGVECTOR


MVP architecture is a modular monolith.

Do not introduce microservices unless explicitly
required.


==================================================
5. REPOSITORY STRUCTURE
==================================================

pathfinder-ai/

├── frontend/
│
├── backend/
│
├── scripts/
│
├── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
├── README.md
└── ...


Backend:

backend/
└── app/
    ├── api/
    ├── core/
    ├── db/
    ├── models/
    ├── schemas/
    ├── services/
    ├── repositories/
    ├── ai/
    ├── rag/
    ├── recommender/
    ├── adaptive/
    └── main.py


Frontend:

frontend/
└── src/
    ├── app/
    ├── layouts/
    ├── pages/
    ├── components/
    ├── features/
    ├── api/
    ├── hooks/
    ├── types/
    ├── lib/
    └── utils/


==================================================
6. DOCUMENTATION
==================================================

The repository must contain:

docs/

├── PROJECT_CONTEXT.md
├── PRODUCT_REQ.md
├── TECHNICAL.md
├── AI_ARCH.md
├── DATABASE_SPEC.md
├── API_SPEC.md
├── AI_SPEC.md
├── FRONTEND_SPEC.md
├── IMPLEMENTATION_PLAN.md
├── TESTING_SPEC.md
├── SEED_DATA_SPEC.md
├── DEPLOYMENT_SPEC.md
├── SECURITY_SPEC.md
└── README_SPEC.md


These documents are the implementation source
of truth.

If code conflicts with documentation:

stop and resolve the conflict.

Do not silently invent a new architecture.


==================================================
7. PREREQUISITES
==================================================

Required:

Node.js
npm
Python
PostgreSQL
pgvector


Recommended:

Git
Docker


Verify:

node --version

npm --version

python --version

psql --version


==================================================
8. DATABASE REQUIREMENTS
==================================================

PostgreSQL must support:

- foreign keys
- JSONB
- indexes
- vector embeddings


Enable:

pgvector


Verify before application startup.


==================================================
9. CLONE PROJECT
==================================================

Example:

git clone <repository-url>

cd pathfinder-ai


==================================================
10. BACKEND SETUP
==================================================

Enter:

cd backend


Create virtual environment:

python -m venv .venv


Activate:

Windows:

.venv\Scripts\activate


Linux/macOS:

source .venv/bin/activate


Install dependencies:

pip install -r requirements.txt


==================================================
11. BACKEND ENVIRONMENT
==================================================

Create:

backend/.env


Copy:

.env.example


Configure:

APP_ENV
APP_NAME
APP_VERSION

DATABASE_URL

SECRET_KEY

CORS_ORIGINS

LLM_PROVIDER
LLM_MODEL
LLM_API_KEY

EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_API_KEY

AI_TIMEOUT_SECONDS
AI_MAX_RETRIES
AI_MAX_TOKENS
AI_TEMPERATURE

RAG_TOP_K

RATE_LIMIT_ENABLED

LOG_LEVEL


Never commit:

backend/.env


==================================================
12. DATABASE SETUP
==================================================

Create database:

pathfinder


Example:

CREATE DATABASE pathfinder;


Enable vector extension:

CREATE EXTENSION IF NOT EXISTS vector;


The exact command may vary depending on
PostgreSQL installation.


==================================================
13. DATABASE MIGRATION
==================================================

From backend:

alembic upgrade head


Expected:

All application tables created.


==================================================
14. SEED DATA
==================================================

Run:

python scripts/seed.py


This creates:

roles
skills
dependencies
role requirements
resources
projects
assessments
questions


Seed must be idempotent.


==================================================
15. SEED VALIDATION
==================================================

Run:

python scripts/validate_seed.py


Validation must confirm:

- foreign keys
- skill mappings
- role mappings
- dependencies
- no dependency cycles
- resources
- projects
- assessments
- questions


==================================================
16. START BACKEND
==================================================

Run:

uvicorn app.main:app --reload


Expected:

http://localhost:8000


Health:

GET /health


API documentation:

/docs


OpenAPI:

/openapi.json


==================================================
17. FRONTEND SETUP
==================================================

From project root:

cd frontend


Install:

npm install


Create:

.env


Configure:

VITE_API_BASE_URL=http://localhost:8000


==================================================
18. START FRONTEND
==================================================

Run:

npm run dev


Expected:

http://localhost:5173


==================================================
19. FRONTEND BUILD
==================================================

Run:

npm run build


Expected:

Production build generated successfully.


==================================================
20. FRONTEND PREVIEW
==================================================

Run:

npm run preview


Use this to test the production build locally.


==================================================
21. COMPLETE LOCAL STARTUP
==================================================

Terminal 1:

Start PostgreSQL


Terminal 2:

cd backend

activate virtual environment

alembic upgrade head

python scripts/seed.py

uvicorn app.main:app --reload


Terminal 3:

cd frontend

npm install

npm run dev


Then open:

http://localhost:5173


==================================================
22. FIRST USER FLOW
==================================================

After startup:

1. Open landing page.
2. Register.
3. Login.
4. Complete onboarding.
5. Enter goal.
6. Confirm learner profile.
7. View skill gaps.
8. Generate roadmap.
9. Open recommendation.
10. View explanation.
11. Start learning.
12. Take assessment.
13. Submit assessment.
14. View result.
15. Observe adaptive update.
16. Return to dashboard.
17. Ask AI Assistant.


==================================================
23. API STRUCTURE
==================================================

Base:

/api/v1


Main groups:

/auth
/profile
/skills
/goals
/skill-gaps
/resources
/recommendations
/roadmaps
/assessments
/progress
/assistant


==================================================
24. AUTH API
==================================================

Register:

POST /api/v1/auth/register


Login:

POST /api/v1/auth/login


Current user:

GET /api/v1/auth/me


Logout:

POST /api/v1/auth/logout


==================================================
25. PROFILE API
==================================================

Examples:

GET /api/v1/profile

PUT /api/v1/profile

GET /api/v1/profile/skills

POST /api/v1/profile/skills

PUT /api/v1/profile/skills/{skill_id}

DELETE /api/v1/profile/skills/{skill_id}


Exact endpoint contracts are defined in:

docs/API_SPEC.md


==================================================
26. GOAL API
==================================================

Goal analysis:

POST /api/v1/ai/analyze-goal


Input:

natural-language goal


Output:

validated structured goal information.


The LLM output must pass schema validation.


==================================================
27. SKILL GAP API
==================================================

GET:

/api/v1/skill-gaps


Returns:

current skills
required skills
gaps
priority
dependencies


Business logic is server-side.


==================================================
28. RECOMMENDATION API
==================================================

GET:

/api/v1/recommendations


Returns:

eligible resources
ranking
explanation


Recommendation ranking must be generated
by the recommendation engine.


==================================================
29. ROADMAP API
==================================================

Generate:

POST /api/v1/roadmaps/generate


Current:

GET /api/v1/roadmaps/current


Start:

POST /api/v1/roadmaps/items/{id}/start


Complete:

POST /api/v1/roadmaps/items/{id}/complete


==================================================
30. ASSESSMENT API
==================================================

Get assessment:

GET /api/v1/assessments/{id}


Submit:

POST /api/v1/assessments/{id}/submit


Results:

GET /api/v1/assessments/{id}/result


Correct answers must never be exposed before
submission.


==================================================
31. PROGRESS API
==================================================

Overall:

GET /api/v1/progress


Skill progress:

GET /api/v1/progress/skills


Next action:

GET /api/v1/progress/next-action


==================================================
32. ASSISTANT API
==================================================

Chat:

POST /api/v1/assistant/chat


The assistant uses:

learner context
skill gaps
roadmap
recommendations
relevant resources
assessment state


It must not access another learner's data.


==================================================
33. AI ARCHITECTURE
==================================================

AI must be abstracted behind provider interfaces.

Example:

LLMProvider

EmbeddingProvider


Do not directly call provider-specific APIs
through random application files.


==================================================
34. GOAL ANALYSIS
==================================================

Flow:

Natural Language
 ↓
LLM
 ↓
Structured Output
 ↓
Schema Validation
 ↓
Business Validation
 ↓
User Confirmation
 ↓
Database


Never:

LLM
 ↓
Database


==================================================
35. RECOMMENDATION ENGINE
==================================================

Flow:

Learner State
 ↓
Skill Gaps
 ↓
Prerequisites
 ↓
Candidate Resources
 ↓
Filtering
 ↓
Deterministic Scoring
 ↓
Semantic Ranking
 ↓
Diversity
 ↓
Explanation


Deterministic ranking must remain testable.


==================================================
36. RECOMMENDATION WEIGHTS
==================================================

Default:

Skill Gap Relevance:

30%


Prerequisite Fit:

20%


Goal Relevance:

15%


Difficulty Fit:

15%


Time Fit:

10%


Preference Fit:

10%


Total:

100%


==================================================
37. ROADMAP ENGINE
==================================================

Flow:

Role
 ↓
Required Skills
 ↓
Current Skills
 ↓
Skill Gaps
 ↓
Dependency Graph
 ↓
Prerequisite Validation
 ↓
Topological Ordering
 ↓
Roadmap


Do not simply sort skills by gap size.


==================================================
38. ADAPTIVE LEARNING
==================================================

Flow:

Assessment
 ↓
Score
 ↓
Mastery
 ↓
Weak Skill
 ↓
Intervention
 ↓
Roadmap Update
 ↓
Dashboard Update


Example:

35% Model Evaluation


may result in:

Model Evaluation Refresher
 ↓
Practice Assessment
 ↓
Model Comparison Project
 ↓
Reassessment


==================================================
39. AI ASSISTANT
==================================================

The assistant should answer questions such as:

"What should I study today?"

"Why was this recommended?"

"Why do I need statistics first?"

"What should I do after this assessment?"

"Explain my biggest skill gap."


Responses must be grounded in actual
learner context.


==================================================
40. RAG
==================================================

RAG flow:

Question
 ↓
Context Builder
 ↓
Embedding
 ↓
Vector Retrieval
 ↓
Metadata Filtering
 ↓
Context Assembly
 ↓
LLM
 ↓
Grounded Response


Do not retrieve unrelated or unauthorized
learner information.


==================================================
41. SECURITY
==================================================

Required:

Authentication
Authorization
Ownership validation
Input validation
Rate limiting
Secure password hashing
Secret management
HTTPS in production
Safe error responses
Prompt injection protection
RAG isolation


==================================================
42. DATA OWNERSHIP
==================================================

Never trust:

user_id
learner_id

from client request bodies.

Use authenticated identity.


==================================================
43. ASSESSMENT SECURITY
==================================================

Frontend receives:

questions
options


Frontend does NOT receive:

correct answers
answer key


Backend calculates:

score
mastery
pass/fail


==================================================
44. ENVIRONMENT VARIABLES
==================================================

Development:

.env


Testing:

test environment configuration


Production:

hosting secret configuration


Never commit real values.


==================================================
45. TESTING COMMANDS
==================================================

Backend unit tests:

pytest tests/unit


Backend integration:

pytest tests/integration


API:

pytest tests/api


AI:

pytest tests/ai


Security:

pytest tests/security


All backend:

pytest


==================================================
46. FRONTEND TESTING
==================================================

Run:

npm test


or configured equivalent.

Verify:

components
forms
routing
loading
errors
API state


==================================================
47. E2E TESTING
==================================================

Run Playwright:

npx playwright test


Critical journey:

Landing
 ↓
Register
 ↓
Onboarding
 ↓
Goal
 ↓
Skill Gap
 ↓
Roadmap
 ↓
Recommendation
 ↓
Assessment
 ↓
Adaptive Update
 ↓
Dashboard
 ↓
Assistant


==================================================
48. LINTING
==================================================

Frontend:

npm run lint


Backend:

configured Python linter


Lint must pass before release.


==================================================
49. TYPE CHECKING
==================================================

Frontend:

TypeScript compiler


Example:

npm run typecheck


Backend:

Pydantic / static typing checks where configured.


==================================================
50. BUILD VALIDATION
==================================================

Before release:

Frontend build must pass.

Backend application must start.

Database migrations must pass.

Seed validation must pass.

Critical tests must pass.


==================================================
51. DOCKER DEVELOPMENT
==================================================

Optional.

If Docker Compose is implemented:

Services:

postgres
backend
frontend


Example:

docker compose up


Do not make Docker mandatory if local
environment already works without it.


==================================================
52. PRODUCTION DEPLOYMENT
==================================================

Production architecture:

Frontend
 ↓
HTTPS
 ↓
FastAPI
 ↓
PostgreSQL + pgvector
 ↓
LLM / Embedding providers


Follow:

docs/DEPLOYMENT_SPEC.md


==================================================
53. PRODUCTION CHECKLIST
==================================================

[ ] environment configured
[ ] secrets configured
[ ] database available
[ ] pgvector enabled
[ ] migrations applied
[ ] seed catalog validated
[ ] backend deployed
[ ] health check passes
[ ] frontend deployed
[ ] API URL configured
[ ] CORS configured
[ ] HTTPS enabled
[ ] rate limiting enabled
[ ] logging enabled
[ ] backup configured
[ ] smoke test passed
[ ] E2E test passed


==================================================
54. TROUBLESHOOTING
==================================================

Problem:

Backend cannot connect to database.

Check:

DATABASE_URL
PostgreSQL running
credentials
database name
network
pgvector


--------------------------------------------------

Problem:

Frontend cannot call backend.

Check:

VITE_API_BASE_URL
backend running
CORS
HTTPS


--------------------------------------------------

Problem:

AI goal analysis fails.

Check:

LLM_PROVIDER
LLM_MODEL
LLM_API_KEY
timeout
provider availability


--------------------------------------------------

Problem:

RAG returns no results.

Check:

embedding configuration
vector extension
embedded resources
metadata filters
vector index


--------------------------------------------------

Problem:

Roadmap is empty.

Check:

role
role-skill mappings
learner profile
skill gaps
dependencies
eligible resources


--------------------------------------------------

Problem:

Assessment does not update roadmap.

Check:

assessment result
mastery calculation
adaptive service
transaction
roadmap update


==================================================
55. DEVELOPMENT RULES
==================================================

Never:

- hardcode learner-specific results
- hardcode recommendation ranking
- hardcode assessment score
- bypass authentication
- bypass authorization
- expose secrets
- expose assessment answers
- fabricate resource URLs
- ignore failing tests
- silently swallow errors


==================================================
56. CODE CHANGE WORKFLOW
==================================================

Before modifying code:

1. Read relevant specification.
2. Inspect current implementation.
3. Identify dependencies.
4. Implement smallest complete change.
5. Run tests.
6. Fix failures.
7. Verify integration.
8. Update documentation if required.


==================================================
57. GIT WORKFLOW
==================================================

Use meaningful commits.

Examples:

Initialize project

Setup database

Implement authentication

Implement learner profile

Implement skill engine

Implement recommendation engine

Implement roadmap

Implement assessments

Implement adaptive learning

Implement dashboard

Implement assistant

Add security controls

Add tests


Avoid one giant commit containing
the entire application.


==================================================
58. DEMO ACCOUNT
==================================================

If demo account is enabled:

Name:

Demo Learner


Email:

demo@pathfinder.local


Role:

AI/ML Engineer


The account must be clearly identified
as demo data.

Never use real personal information.


==================================================
59. PRIMARY DEMO SCENARIO
==================================================

Goal:

"I want to become an AI/ML Engineer."


Current profile:

Python = 75
SQL = 60
Statistics = 35
Probability = 40
Data Processing = 55
Machine Learning = 30
Model Evaluation = 25
Git = 60
APIs = 40
Docker = 20


Expected behavior:

System identifies meaningful gaps.

System calculates recommendations.

System generates dependency-aware roadmap.


==================================================
60. ADAPTIVE DEMO
==================================================

Learner takes:

Model Evaluation Assessment


Score:

30%


Expected:

Weak mastery.


System creates:

Model Evaluation refresher
Practice
Model comparison project
Reassessment


Dashboard:

Next Best Action

should reflect the intervention.


==================================================
61. SUCCESS DEMO
==================================================

Learner later achieves:

90%

in Model Evaluation.


Expected:

Skill becomes:

MASTERED


Roadmap:

allows progression to next eligible
dependent milestone.


==================================================
62. COMPLETE DEMO SCRIPT
==================================================

Demo presenter should show:

1. Landing page
2. Register
3. Goal
4. AI goal analysis
5. Profile confirmation
6. Skill gaps
7. Dependency graph
8. Roadmap
9. Recommendation
10. "Why this?"
11. Resource
12. Assessment
13. Weak result
14. Adaptive update
15. Updated roadmap
16. Dashboard
17. Next best action
18. AI Assistant


==================================================
63. DEMO QUESTIONS
==================================================

The presenter should be able to ask:

"Why is this recommended?"

"What is my biggest skill gap?"

"Why do I need statistics first?"

"What should I learn today?"

"What changed after my assessment?"


The assistant must answer using actual
application context.


==================================================
64. README QUALITY RULE
==================================================

The README must be understandable by:

- developer
- evaluator
- teammate
- future maintainer


Avoid unexplained jargon.

When technical terminology is necessary,
explain it briefly.


==================================================
65. DOCUMENTATION SOURCE OF TRUTH
==================================================

Use:

PRODUCT_REQ.md

for product requirements.

TECHNICAL.md

for technical architecture.

DATABASE_SPEC.md

for database.

API_SPEC.md

for API contracts.

AI_SPEC.md

for AI behavior.

FRONTEND_SPEC.md

for UI.

IMPLEMENTATION_PLAN.md

for development order.

TESTING_SPEC.md

for testing.

SEED_DATA_SPEC.md

for seed data.

DEPLOYMENT_SPEC.md

for deployment.

SECURITY_SPEC.md

for security.


==================================================
66. CONFLICT RESOLUTION
==================================================

If two documents appear inconsistent:

DO NOT silently choose one.

Identify:

1. conflict
2. affected feature
3. likely source of truth
4. required resolution


Then update documentation before implementing
a potentially conflicting feature.


==================================================
67. PROJECT STATUS
==================================================

README should contain:

Project Status:

MVP / Prototype

Then optionally:

Current phase
Known limitations
Completed features
Future features


Do not claim features are complete
unless they actually work.


==================================================
68. KNOWN LIMITATIONS
==================================================

Document limitations honestly.

Examples:

- AI provider dependency
- limited initial role catalog
- curated initial resources
- limited assessment question bank
- no resume analysis in MVP
- no GitHub analysis in MVP
- no voice assistant in MVP


Do not hide limitations.


==================================================
69. FUTURE ROADMAP
==================================================

Future versions may include:

Resume parsing
GitHub profile analysis
Certification planning
Career market intelligence
Voice assistant
More career roles
More resources
Advanced learning analytics
Gamification


These are not required for MVP.


==================================================
70. PROJECT PHILOSOPHY
==================================================

PathFinder is not:

a generic chatbot
a course marketplace
a static roadmap generator
a fake analytics dashboard


PathFinder is:

an intelligent learning navigation system.


Core loop:

UNDERSTAND
 ↓
ANALYZE
 ↓
IDENTIFY
 ↓
RECOMMEND
 ↓
EXPLAIN
 ↓
ASSESS
 ↓
ADAPT
 ↓
GUIDE


==================================================
71. FINAL DEVELOPER CHECKLIST
==================================================

Before saying:

"PathFinder is complete"

verify:

[ ] application starts
[ ] database starts
[ ] migrations pass
[ ] seed passes
[ ] backend starts
[ ] frontend starts
[ ] registration works
[ ] login works
[ ] onboarding works
[ ] goal analysis works
[ ] profile works
[ ] skill gaps work
[ ] recommendations work
[ ] roadmap works
[ ] resource works
[ ] assessment works
[ ] scoring works
[ ] adaptive update works
[ ] dashboard works
[ ] assistant works
[ ] authorization works
[ ] security tests pass
[ ] E2E passes
[ ] production build passes


==================================================
72. FINAL USER JOURNEY
==================================================

The complete product experience must be:

I have a goal.
        ↓
PathFinder understands it.
        ↓
PathFinder understands my current state.
        ↓
PathFinder identifies my gaps.
        ↓
PathFinder understands dependencies.
        ↓
PathFinder recommends what matters.
        ↓
PathFinder explains why.
        ↓
PathFinder gives me a sequence.
        ↓
I learn.
        ↓
I get assessed.
        ↓
PathFinder understands my result.
        ↓
PathFinder adapts my path.
        ↓
PathFinder tells me what to do next.


==================================================
73. FINAL DEFINITION OF DONE
==================================================

The repository is ready for handoff when:

[ ] README is complete
[ ] setup instructions work
[ ] environment variables documented
[ ] database setup documented
[ ] migration commands documented
[ ] seed commands documented
[ ] backend commands documented
[ ] frontend commands documented
[ ] testing commands documented
[ ] deployment documented
[ ] security documented
[ ] API documented
[ ] AI architecture documented
[ ] demo flow documented
[ ] known limitations documented


==================================================
END OF README_SPEC.md
==================================================