# PathFinder AI — Deployment Specification

Document: DEPLOYMENT_SPEC.md
Version: 1.0
Status: Implementation Specification
Project: PathFinder AI

==================================================
1. PURPOSE
==================================================

This document defines the deployment architecture,
environment configuration, database deployment,
frontend deployment, backend deployment, security,
health checks, migrations, logging and production
readiness requirements for PathFinder AI.

The deployment must remain simple.

MVP deployment must use a modular monolith.

Do NOT introduce:

- Kubernetes
- microservices
- service mesh
- event buses
- distributed queues
- unnecessary cloud infrastructure

unless explicitly required later.


==================================================
2. TARGET DEPLOYMENT ARCHITECTURE
==================================================

Recommended:

                 USER
                   │
                   ▼
              FRONTEND
                   │
                   ▼
               HTTPS API
                   │
                   ▼
                FASTAPI
                   │
          ┌────────┼────────┐
          │        │        │
          ▼        ▼        ▼
       DOMAIN     AI       RAG
       SERVICES  SERVICES  SERVICES
          │        │        │
          └────────┼────────┘
                   │
                   ▼
             PostgreSQL
               + pgvector


==================================================
3. DEPLOYMENT COMPONENTS
==================================================

Required:

1. Frontend
2. Backend
3. PostgreSQL
4. pgvector
5. LLM provider
6. Embedding provider

Optional:

Object storage
External monitoring
CDN


==================================================
4. ENVIRONMENTS
==================================================

Maintain:

development
testing
production

Each environment must have independent
configuration.

Never use production credentials locally.


==================================================
5. REPOSITORY STRUCTURE
==================================================

pathfinder-ai/

  frontend/
  backend/

  scripts/
  tests/
  docs/

  .env.example
  .gitignore
  README.md


==================================================
6. ENVIRONMENT VARIABLES
==================================================

Backend configuration:

APP_ENV=
APP_NAME=
APP_VERSION=

DATABASE_URL=

SECRET_KEY=

CORS_ORIGINS=

LLM_PROVIDER=
LLM_MODEL=
LLM_API_KEY=

EMBEDDING_PROVIDER=
EMBEDDING_MODEL=
EMBEDDING_API_KEY=

AI_TIMEOUT_SECONDS=
AI_MAX_RETRIES=
AI_MAX_TOKENS=

AI_TEMPERATURE=

RAG_TOP_K=

RATE_LIMIT_ENABLED=

LOG_LEVEL=


==================================================
7. ENVIRONMENT VARIABLE RULES
==================================================

Never commit:

LLM_API_KEY
EMBEDDING_API_KEY
SECRET_KEY
DATABASE_URL containing credentials

to Git.

Commit only:

.env.example


==================================================
8. .ENV.EXAMPLE
==================================================

Create:

.env.example

Example structure:

APP_ENV=development
APP_NAME=PathFinder AI
APP_VERSION=1.0.0

DATABASE_URL=postgresql://user:password@localhost:5432/pathfinder

SECRET_KEY=replace_me

CORS_ORIGINS=http://localhost:5173

LLM_PROVIDER=replace_me
LLM_MODEL=replace_me
LLM_API_KEY=replace_me

EMBEDDING_PROVIDER=replace_me
EMBEDDING_MODEL=replace_me
EMBEDDING_API_KEY=replace_me

AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=2
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.2

RAG_TOP_K=5

RATE_LIMIT_ENABLED=true

LOG_LEVEL=INFO


==================================================
9. DATABASE DEPLOYMENT
==================================================

Use:

PostgreSQL

with:

pgvector


Database must support:

- relational data
- JSONB
- foreign keys
- indexes
- vector embeddings


==================================================
10. DATABASE PROVISIONING
==================================================

Production database must be provisioned
before backend deployment.

Verify:

PostgreSQL version
pgvector extension
database user
database permissions
connection string
SSL where required


==================================================
11. PGVECTOR
==================================================

Verify extension:

vector

is installed.

Application startup must not silently assume
vector support exists.

If vector extension is unavailable:

RAG/semantic search must fail clearly.

Do not silently fall back to fake semantic search.


==================================================
12. DATABASE MIGRATIONS
==================================================

Use:

Alembic

Never manually modify production schema.

Deployment flow:

Deploy code
 ↓
Run migration
 ↓
Verify migration
 ↓
Start application


==================================================
13. MIGRATION SAFETY
==================================================

Before production migration:

1. Backup database.
2. Review migration.
3. Test migration in staging.
4. Run migration.
5. Verify schema.
6. Start application.


==================================================
14. DATABASE BACKUP
==================================================

Production database must have backups.

At minimum:

Regular automated backups
+
manual backup before major migration


Backup retention must be configured according
to hosting provider capabilities.


==================================================
15. DATABASE CONNECTION
==================================================

Backend must use connection pooling.

Do not open a new database connection for
every request manually.

Configure:

pool size
maximum overflow
connection timeout


==================================================
16. BACKEND DEPLOYMENT
==================================================

Backend:

FastAPI

Production server:

ASGI server

Example:

uvicorn

or equivalent production ASGI configuration.


==================================================
17. BACKEND START COMMAND
==================================================

Example:

uvicorn app.main:app
--host 0.0.0.0
--port $PORT


Actual hosting platform command may vary.


==================================================
18. BACKEND HEALTH CHECK
==================================================

Create:

GET /health

Expected:

HTTP 200

Response:

{
  "status": "ok"
}


==================================================
19. READINESS CHECK
==================================================

Create:

GET /health/ready

This should verify required dependencies.

Possible checks:

database connection
required application configuration


Do not perform expensive AI requests
inside health checks.


==================================================
20. LIVENESS CHECK
==================================================

Create:

GET /health/live

Expected:

HTTP 200

Purpose:

Confirm process is alive.

It should be lightweight.


==================================================
21. STARTUP VALIDATION
==================================================

At startup validate:

Required environment variables
Database connectivity
Required configuration

Do not call expensive LLM APIs during startup.


==================================================
22. FRONTEND DEPLOYMENT
==================================================

Frontend:

React + Vite

Build:

npm run build

Output:

dist/


==================================================
23. FRONTEND ENVIRONMENT
==================================================

Frontend should only receive public configuration.

Example:

VITE_API_BASE_URL=

Never expose:

LLM API key
database credentials
backend secret
private provider credentials


==================================================
24. FRONTEND BUILD
==================================================

Production process:

Install dependencies
 ↓
Type check
 ↓
Lint
 ↓
Test
 ↓
Build
 ↓
Deploy dist


==================================================
25. API BASE URL
==================================================

Development:

http://localhost:8000

Production:

HTTPS backend URL

Do not hardcode production URLs
inside components.


==================================================
26. CORS
==================================================

Backend must allow only required origins.

Development:

http://localhost:5173

Production:

actual frontend domain


Never use:

allow_origins=["*"]

for production when credentials
or authenticated requests are involved.


==================================================
27. HTTPS
==================================================

Production must use HTTPS.

Do not transmit:

credentials
authentication data
learner information

over plain HTTP.


==================================================
28. SECURITY HEADERS
==================================================

Where supported, configure appropriate
security headers.

Examples:

Content-Security-Policy
X-Content-Type-Options
Referrer-Policy
Strict-Transport-Security

Exact configuration depends on hosting
architecture.


==================================================
29. AUTHENTICATION SECURITY
==================================================

Production authentication must use:

secure credentials
HTTPS
appropriate token/session handling

Never:

log authentication tokens
place secrets in frontend source
return password hashes


==================================================
30. PASSWORD SECURITY
==================================================

Passwords must be stored using a strong
password hashing algorithm.

Never store plaintext passwords.


==================================================
31. SECRET MANAGEMENT
==================================================

Production secrets must be stored using:

hosting provider environment variables
or
dedicated secret manager

Never:

Git
README
frontend source
database seed
test fixtures


==================================================
32. AI PROVIDER CONFIGURATION
==================================================

AI provider is configured through:

LLM_PROVIDER
LLM_MODEL
LLM_API_KEY

The application must not hardcode
provider-specific assumptions into domain logic.


==================================================
33. EMBEDDING CONFIGURATION
==================================================

Embedding configuration:

EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_API_KEY


Embedding generation must remain isolated
from recommendation business logic.


==================================================
34. AI FAILURE IN PRODUCTION
==================================================

If LLM unavailable:

Goal analysis:

manual fallback where supported.

Recommendation:

deterministic recommendation engine continues.

Progress:

continues.

Skill gaps:

continues.

Prerequisites:

continues.

Authentication:

continues.


==================================================
35. AI TIMEOUT
==================================================

Production AI requests must have a timeout.

Example:

AI_TIMEOUT_SECONDS=30


Never allow indefinitely hanging AI requests.


==================================================
36. AI RETRIES
==================================================

Maximum:

2 retries

Retries should occur only for transient
failures.

Do not retry:

invalid input
authorization failure
validation errors


==================================================
37. RATE LIMITING
==================================================

Protect expensive endpoints.

High-priority:

POST /api/v1/ai/analyze-goal

POST /api/v1/assistant/chat

Recommendation generation if expensive


When exceeded:

HTTP 429


==================================================
38. DATABASE RATE / LOAD PROTECTION
==================================================

Avoid excessive:

roadmap generation
recommendation regeneration
embedding generation

Use caching where appropriate.

Do not cache personalized responses
across users.


==================================================
39. LOGGING
==================================================

Production logging must include:

timestamp
level
request ID
endpoint
HTTP status
latency
error code


Do not log:

passwords
API keys
tokens
full sensitive learner data


==================================================
40. LOG LEVELS
==================================================

Development:

DEBUG / INFO


Testing:

INFO


Production:

INFO


Temporary DEBUG logging must not be enabled
in production without reason.


==================================================
41. ERROR HANDLING
==================================================

Production API must return safe errors.

Example:

{
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "AI service is temporarily unavailable."
  }
}


Never return:

stack trace
SQL query
filesystem path
secret
provider credentials


==================================================
42. ERROR MONITORING
==================================================

Where monitoring is available, track:

5xx errors
4xx spikes
AI failures
database failures
slow requests
authentication failures


==================================================
43. REQUEST ID
==================================================

Each API request should have a request ID.

Use it for:

logs
debugging
support

Example:

X-Request-ID


==================================================
44. OBSERVABILITY
==================================================

Track:

API latency
database latency
AI latency
AI failure rate
recommendation generation failures
assessment failures
5xx rate


Avoid collecting unnecessary personal data.


==================================================
45. FRONTEND ERROR HANDLING
==================================================

Frontend must handle:

401
403
404
409
422
429
500
503


Examples:

401:

Redirect to login where appropriate.


403:

"You do not have permission to access this."


404:

"The requested resource was not found."


429:

"Too many requests. Please try again shortly."


503:

"PathFinder is temporarily unavailable."


==================================================
46. DEPLOYMENT ORDER
==================================================

Production deployment order:

1. Provision database.
2. Enable pgvector.
3. Configure environment.
4. Run migrations.
5. Validate database.
6. Deploy backend.
7. Verify health.
8. Deploy frontend.
9. Configure API URL.
10. Verify CORS.
11. Run smoke tests.
12. Verify complete demo flow.


==================================================
47. ZERO-DOWNTIME CONSIDERATION
==================================================

For MVP:

Simple deployment is acceptable.

However:

Avoid migrations that immediately destroy
data required by the currently deployed
application.

For breaking schema changes:

1. Add new structure.
2. Deploy compatible code.
3. Migrate data.
4. Remove old structure later.


==================================================
48. ROLLBACK STRATEGY
==================================================

If deployment fails:

1. Stop rollout.
2. Inspect health check.
3. Inspect logs.
4. Roll back application if necessary.
5. Restore database only if required.
6. Verify previous version.


Do not automatically roll back database
destructively.


==================================================
49. APPLICATION VERSION
==================================================

Store application version.

Example:

APP_VERSION=1.0.0


Expose safely through:

GET /health

or:

GET /version


Example:

{
  "version": "1.0.0"
}


==================================================
50. SMOKE TESTS
==================================================

After deployment verify:

GET /health
GET /health/live
GET /health/ready


Then:

Register
Login
Create Goal
View Skill Gaps
Generate Roadmap
Open Resource
Take Assessment
View Result
View Dashboard
Ask Assistant


==================================================
51. PRODUCTION SMOKE TEST
==================================================

Minimum:

1. Landing page loads.
2. Register works.
3. Login works.
4. Onboarding works.
5. Goal analysis works.
6. Skill gap loads.
7. Roadmap loads.
8. Recommendation loads.
9. Assessment loads.
10. Result loads.
11. Adaptive update occurs.
12. Dashboard updates.
13. Assistant responds.


==================================================
52. DEMO DEPLOYMENT
==================================================

The deployed demo must contain:

Curated catalog data.

Optional:

Demo learner.

If demo account exists:

Clearly identify:

DEMO ACCOUNT


Do not mix demo data with real user data.


==================================================
53. DEMO ACCOUNT SECURITY
==================================================

If a public demo account is provided:

Do not use:

real personal email
real password
real learner information
production credentials


Demo account must have restricted
appropriate permissions.


==================================================
54. DATABASE SEED IN PRODUCTION
==================================================

Do not blindly run development seed scripts
against production.

Production seed must:

- insert catalog data safely
- be idempotent
- never delete real learner data
- never overwrite learner progress


==================================================
55. STATIC ASSETS
==================================================

Optimize:

images
icons
fonts
bundles


Avoid unnecessarily large assets.

Use lazy loading where useful.


==================================================
56. FRONTEND PERFORMANCE
==================================================

Monitor:

initial load
bundle size
API waterfalls
unnecessary requests


Avoid loading AI/chat functionality
when not required for initial page.


==================================================
57. DATABASE PERFORMANCE
==================================================

Verify indexes for frequent queries:

learner_id
role_id
skill_id
resource_id
roadmap_id
assessment_id


Vector search must have appropriate
pgvector indexing when dataset size requires it.


==================================================
58. BACKEND PERFORMANCE
==================================================

Avoid:

N+1 queries
unnecessary database calls
repeated AI calls
repeated embedding generation


Use:

eager loading
batch operations
caching
connection pooling

where appropriate.


==================================================
59. CACHING
==================================================

Good candidates:

skill catalog
role catalog
resource catalog
static configuration


Do not blindly cache:

learner progress
assessment results
personalized roadmap
personalized recommendations


==================================================
60. DATA PRIVACY
==================================================

Only collect information required for
PathFinder functionality.

Do not send unnecessary learner information
to AI providers.

AI context should contain only relevant
information.


==================================================
61. AI DATA BOUNDARY
==================================================

Before sending context to LLM:

Filter:

passwords
tokens
authentication information
unrelated learner records
other learners' data


Only send:

goal
skills
skill gaps
roadmap context
relevant resources
relevant assessment information


==================================================
62. BACKUP & RECOVERY TEST
==================================================

Test:

Database backup
 ↓
Restore to separate test database
 ↓
Run application
 ↓
Verify core data


A backup is not considered valid until
restore has been tested.


==================================================
63. MIGRATION TEST IN STAGING
==================================================

Every production migration should first run
against a staging/test database.

Verify:

application starts
queries work
old data remains valid
new fields work


==================================================
64. CI/CD PIPELINE
==================================================

Recommended pipeline:

Push
 ↓
Install
 ↓
Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
API Tests
 ↓
Frontend Build
 ↓
Backend Build
 ↓
Optional E2E
 ↓
Deploy


Do not deploy if critical tests fail.


==================================================
65. CI/CD SECRETS
==================================================

CI secrets must be stored in the CI platform.

Never write:

API keys
passwords
tokens

into workflow files.


==================================================
66. DOCKER
==================================================

Docker may be used for reproducible
development/deployment.

Recommended:

backend Dockerfile
frontend Dockerfile if required


Keep images minimal.

Do not introduce Docker merely for
complexity if hosting does not require it.


==================================================
67. LOCAL DOCKER DEVELOPMENT
==================================================

Optional:

docker compose

Services:

postgres

backend

frontend


For development convenience only.

Production architecture may differ.


==================================================
68. LOCAL SETUP
==================================================

Required documentation:

1. Clone repository.
2. Install dependencies.
3. Configure .env.
4. Start PostgreSQL.
5. Enable pgvector.
6. Run migrations.
7. Run seed.
8. Start backend.
9. Start frontend.


==================================================
69. LOCAL DATABASE COMMANDS
==================================================

Example:

Run migrations:

alembic upgrade head


Seed:

python scripts/seed.py


Validate:

python scripts/validate_seed.py


==================================================
70. LOCAL BACKEND
==================================================

Example:

uvicorn app.main:app --reload


Expected:

http://localhost:8000


Swagger:

/docs


==================================================
71. LOCAL FRONTEND
==================================================

Example:

npm install

npm run dev


Expected:

http://localhost:5173


==================================================
72. PRODUCTION CONFIGURATION CHECKLIST
==================================================

[ ] APP_ENV=production
[ ] APP_VERSION configured
[ ] DATABASE_URL configured
[ ] SECRET_KEY configured
[ ] CORS configured
[ ] LLM provider configured
[ ] Embedding provider configured
[ ] AI timeout configured
[ ] AI retries configured
[ ] Rate limiting enabled
[ ] LOG_LEVEL configured
[ ] HTTPS enabled
[ ] Database backup configured
[ ] pgvector enabled


==================================================
73. SECURITY CHECKLIST
==================================================

[ ] HTTPS
[ ] Strong password hashing
[ ] Secrets outside Git
[ ] Restricted CORS
[ ] Rate limiting
[ ] Input validation
[ ] Authorization
[ ] User data isolation
[ ] Safe error responses
[ ] No sensitive logs
[ ] Prompt injection protection
[ ] No frontend secrets


==================================================
74. DATABASE CHECKLIST
==================================================

[ ] PostgreSQL running
[ ] pgvector enabled
[ ] migrations applied
[ ] indexes verified
[ ] backups configured
[ ] restore tested
[ ] connection pooling
[ ] seed validation passed


==================================================
75. APPLICATION CHECKLIST
==================================================

[ ] backend starts
[ ] frontend starts
[ ] health check works
[ ] readiness check works
[ ] authentication works
[ ] onboarding works
[ ] roadmap works
[ ] assessment works
[ ] adaptive update works
[ ] dashboard works
[ ] assistant works


==================================================
76. PRODUCTION FAILURE SCENARIOS
==================================================

Test:

Database unavailable

Expected:

safe 503/error behavior


LLM unavailable

Expected:

deterministic features continue.


Embedding provider unavailable

Expected:

semantic search fails gracefully or
deterministic recommendations continue.


Invalid environment variable

Expected:

application fails clearly during startup
rather than operating in a broken state.


==================================================
77. DEPLOYMENT ACCEPTANCE TEST
==================================================

A deployment is accepted only if:

[ ] frontend reachable
[ ] backend reachable
[ ] HTTPS works
[ ] database connected
[ ] pgvector works
[ ] migrations applied
[ ] seed validated
[ ] authentication works
[ ] onboarding works
[ ] skill gaps work
[ ] recommendations work
[ ] roadmap works
[ ] assessment works
[ ] adaptive learning works
[ ] dashboard works
[ ] assistant works
[ ] no critical security issue exists


==================================================
78. FINAL DEPLOYMENT FLOW
==================================================

                 CODE
                   │
                   ▼
                TESTS
                   │
                   ▼
              BUILD
                   │
                   ▼
             DATABASE
                   │
              MIGRATIONS
                   │
                   ▼
              BACKEND
                   │
             HEALTH CHECK
                   │
                   ▼
              FRONTEND
                   │
              SMOKE TEST
                   │
                   ▼
             E2E TEST
                   │
                   ▼
              RELEASE


==================================================
79. FINAL DEFINITION OF DONE
==================================================

PathFinder deployment is complete when:

[ ] development environment works
[ ] testing environment works
[ ] production environment works
[ ] environment variables documented
[ ] secrets secured
[ ] database deployed
[ ] pgvector deployed
[ ] migrations deployed
[ ] backup configured
[ ] restore tested
[ ] backend deployed
[ ] frontend deployed
[ ] health checks work
[ ] CORS configured
[ ] HTTPS enabled
[ ] rate limiting enabled
[ ] logging configured
[ ] monitoring configured where available
[ ] smoke tests pass
[ ] E2E test passes
[ ] demo flow works
[ ] README contains deployment instructions


==================================================
80. FINAL PRINCIPLE
==================================================

Deployment must make the same real PathFinder
application available outside the developer's
machine.

Do NOT create a separate "demo version" that
fakes:

recommendations
roadmaps
assessments
progress
adaptive learning

The deployed system must execute the same
underlying application logic.


==================================================
END OF DEPLOYMENT_SPEC.md
==================================================