# PathFinder AI — Database Specification

**Document:** DATABASE_SPEC.md  
**Version:** 1.0  
**Status:** Implementation Specification  
**Project:** PathFinder AI  
**Database:** PostgreSQL  
**Vector Extension:** pgvector  
**ORM:** SQLAlchemy  
**Migrations:** Alembic  

---

# 1. Purpose

This document defines the complete database architecture for PathFinder AI.

The database must act as the **primary source of truth** for:

- users
- learner profiles
- skills
- career roles
- role requirements
- learner skill state
- skill prerequisites
- learning resources
- projects
- assessments
- roadmaps
- recommendations
- progress
- feedback
- conversations
- roadmap versions

The database must support:

```text
Natural Language Goal
        ↓
Learner Profile
        ↓
Learner Skills
        ↓
Target Role
        ↓
Skill Requirements
        ↓
Skill Gap
        ↓
Prerequisite Graph
        ↓
Recommendations
        ↓
Roadmap
        ↓
Learning Progress
        ↓
Assessment
        ↓
Adaptive Update
        ↓
New Roadmap Version
```

The database must never become a storage layer containing disconnected dashboard values.

---

# 2. Core Database Principles

## 2.1 PostgreSQL

Use PostgreSQL as the primary relational database.

Do not introduce another primary database.

## 2.2 pgvector

Use PostgreSQL + pgvector for semantic retrieval.

Vector embeddings will primarily support:

- resources
- projects
- learning content
- potentially skill descriptions

Semantic similarity is only one recommendation signal. It must not replace structured filtering and recommendation scoring.

## 2.3 UUID Primary Keys

Use UUID primary keys for externally exposed entities.

Preferred SQLAlchemy configuration:

```text
UUID
PRIMARY KEY
DEFAULT gen_random_uuid()
```

Enable the required PostgreSQL extension:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
```

## 2.4 Naming Convention

All database identifiers must use:

```text
snake_case
```

Examples:

```text
learner_profiles
learner_skills
skill_prerequisites
roadmap_items
assessment_results
```

## 2.5 Timestamps

Mutable business entities should normally contain:

```text
created_at
updated_at
```

Use timezone-aware timestamps:

```text
TIMESTAMP WITH TIME ZONE
```

## 2.6 JSONB

Use JSONB only for flexible metadata or structured explanation data.

Do not use JSONB to avoid designing proper relational tables.

Good uses:

```text
learning_preferences
resource metadata
project metadata
recommendation reason
roadmap explanation data
```

Bad use:

```text
storing all learner skills inside one JSONB column
```

---

# 3. Entity Relationship Overview

The primary relationship model is:

```text
users
  │
  └── learner_profiles
          │
          ├── learner_skills ───────── skills
          │                              │
          │                              ├── skill_prerequisites
          │                              │
          │                              ├── role_skills ───── roles
          │                              │
          │                              ├── resource_skills ── resources
          │                              │
          │                              └── project_skills ─── projects
          │
          └── roadmaps
                  │
                  └── roadmap_items
                          │
                          ├── skills
                          ├── resources
                          ├── projects
                          └── assessments

assessments
    │
    ├── assessment_questions
    │
    └── assessment_results
              │
              └── learner skill updates

learners
    │
    ├── progress
    ├── feedback
    ├── recommendations
    └── conversations
              │
              └── conversation_messages

roadmaps
    │
    └── roadmap_versions
```

---

# 4. Required Tables

The MVP database must contain at minimum:

```text
users
learner_profiles
skills
roles
role_skills
learner_skills
skill_prerequisites
resources
resource_skills
projects
project_skills
assessments
assessment_questions
assessment_results
roadmaps
roadmap_items
recommendations
feedback
progress
conversations
conversation_messages
roadmap_versions
```

Do not remove these entities unless the implementation architecture provides an equivalent persistent model.

---

# 5. Table: users

Stores authentication and basic identity information.

```text
users
-----
id UUID PRIMARY KEY
name VARCHAR(120) NOT NULL
email VARCHAR(255) UNIQUE NOT NULL
password_hash TEXT NOT NULL
is_active BOOLEAN NOT NULL DEFAULT TRUE
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Constraints:

```text
email must be unique
password must never be stored in plain text
```

Password hashing must use a secure password hashing algorithm such as Argon2id.

Never store:

```text
plain_password
JWT secret
API keys
LLM keys
```

---

# 6. Table: learner_profiles

One learner should have one primary learner profile.

```text
learner_profiles
----------------
id UUID PRIMARY KEY
user_id UUID UNIQUE NOT NULL
target_role_id UUID NULL
experience_level VARCHAR(30) NULL
daily_study_hours NUMERIC(4,2) NULL
target_duration_weeks INTEGER NULL
learning_preferences JSONB NOT NULL DEFAULT '{}'
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Relationships:

```text
learner_profiles.user_id
    → users.id

learner_profiles.target_role_id
    → roles.id
```

Allowed experience values:

```text
beginner
intermediate
advanced
not_sure
```

`learning_preferences` example:

```json
{
  "content_types": [
    "videos",
    "projects",
    "documentation"
  ],
  "interactive_learning": true
}
```

Do not store the entire learner state as one JSON document.

Structured learner information must remain relational.

---

# 7. Table: skills

Represents the canonical skill catalog.

```text
skills
------
id UUID PRIMARY KEY
name VARCHAR(150) UNIQUE NOT NULL
slug VARCHAR(180) UNIQUE NOT NULL
category VARCHAR(80) NOT NULL
description TEXT
difficulty VARCHAR(30)
estimated_hours NUMERIC(8,2)
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Examples:

```text
Python
SQL
Statistics
Probability
Machine Learning
Deep Learning
Model Evaluation
Docker
MLOps
Generative AI
```

Categories may include:

```text
programming
mathematics
data
machine_learning
deep_learning
engineering
deployment
```

The skill catalog must use canonical skill records.

Do not create duplicate skills such as:

```text
Machine Learning
machine-learning
ML
ML Basics
```

unless they are deliberately modeled as separate concepts.

---

# 8. Table: roles

Represents target career roles.

```text
roles
-----
id UUID PRIMARY KEY
name VARCHAR(150) UNIQUE NOT NULL
slug VARCHAR(180) UNIQUE NOT NULL
description TEXT
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Initial MVP roles should support approximately 6–8 career paths.

Recommended examples:

```text
AI/ML Engineer
Data Scientist
Data Analyst
Backend Developer
Frontend Developer
Full Stack Developer
Cloud Engineer
DevOps Engineer
```

The exact seeded catalog should be maintained through seed data.

---

# 9. Table: role_skills

Many-to-many relationship between roles and required skills.

```text
role_skills
-----------
role_id UUID NOT NULL
skill_id UUID NOT NULL
required_proficiency NUMERIC(5,2) NOT NULL
importance NUMERIC(5,2) NOT NULL
PRIMARY KEY (role_id, skill_id)
```

Foreign keys:

```text
role_id
    → roles.id

skill_id
    → skills.id
```

Constraints:

```text
required_proficiency >= 0
required_proficiency <= 100

importance >= 0
importance <= 1
```

Example:

```text
AI/ML Engineer
    ↓
Python
required_proficiency = 85
importance = 1.0
```

This table is authoritative for target-role requirements.

---

# 10. Table: learner_skills

Stores the learner's current skill state.

```text
learner_skills
--------------
learner_id UUID NOT NULL
skill_id UUID NOT NULL
proficiency NUMERIC(5,2) NOT NULL
source VARCHAR(30) NOT NULL
confidence NUMERIC(5,4)
updated_at TIMESTAMPTZ NOT NULL
PRIMARY KEY (learner_id, skill_id)
```

Foreign keys:

```text
learner_id
    → learner_profiles.id

skill_id
    → skills.id
```

Allowed sources:

```text
self_declared
assessment
imported
inferred
```

Constraints:

```text
proficiency >= 0
proficiency <= 100

confidence >= 0
confidence <= 1
```

Important:

Assessment-derived evidence should generally have higher confidence than unsupported self-declaration.

---

# 11. Table: skill_prerequisites

Represents the directed skill dependency graph.

```text
skill_prerequisites
-------------------
skill_id UUID NOT NULL
prerequisite_skill_id UUID NOT NULL
strength NUMERIC(5,4) NOT NULL DEFAULT 1.0
PRIMARY KEY (skill_id, prerequisite_skill_id)
```

Example:

```text
Machine Learning
    requires
Statistics
```

Therefore:

```text
skill_id = Machine Learning
prerequisite_skill_id = Statistics
```

Constraints:

```text
strength >= 0
strength <= 1
```

Self-reference must be rejected:

```text
skill_id != prerequisite_skill_id
```

The system must prevent invalid prerequisite cycles.

Example invalid cycle:

```text
A → B
B → C
C → A
```

---

# 12. Table: resources

Stores trusted learning resources.

```text
resources
---------
id UUID PRIMARY KEY
title VARCHAR(255) NOT NULL
description TEXT
resource_type VARCHAR(50) NOT NULL
provider VARCHAR(150)
url TEXT NOT NULL
difficulty VARCHAR(30)
estimated_minutes INTEGER
quality_score NUMERIC(5,2)
is_active BOOLEAN NOT NULL DEFAULT TRUE
metadata JSONB NOT NULL DEFAULT '{}'
embedding VECTOR(<EMBEDDING_DIMENSION>) NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Resource types may include:

```text
course
documentation
tutorial
article
video
book
exercise
project
assessment
```

The embedding dimension must be configured through the selected embedding model.

Do not hardcode a dimension unrelated to the actual embedding provider.

Resource records must represent trusted/verified resources.

Do not fabricate resource URLs.

---

# 13. Table: resource_skills

Maps resources to skills.

```text
resource_skills
---------------
resource_id UUID NOT NULL
skill_id UUID NOT NULL
coverage_weight NUMERIC(5,4) NOT NULL
PRIMARY KEY (resource_id, skill_id)
```

Constraints:

```text
coverage_weight >= 0
coverage_weight <= 1
```

Example:

```text
Resource:
Machine Learning Course

Skills:
Python → 0.30
Statistics → 0.70
Machine Learning → 1.00
```

This allows the recommendation engine to understand how strongly a resource covers a skill.

---

# 14. Table: projects

Stores practical projects.

```text
projects
--------
id UUID PRIMARY KEY
title VARCHAR(255) NOT NULL
description TEXT
difficulty VARCHAR(30)
estimated_hours NUMERIC(8,2)
instructions TEXT
metadata JSONB NOT NULL DEFAULT '{}'
embedding VECTOR(<EMBEDDING_DIMENSION>) NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Projects should support project-based learning.

---

# 15. Table: project_skills

Maps projects to skills.

```text
project_skills
--------------
project_id UUID NOT NULL
skill_id UUID NOT NULL
coverage_weight NUMERIC(5,4) NOT NULL
PRIMARY KEY (project_id, skill_id)
```

Constraints:

```text
coverage_weight >= 0
coverage_weight <= 1
```

---

# 16. Table: assessments

Stores assessments associated with skills.

```text
assessments
-----------
id UUID PRIMARY KEY
skill_id UUID NOT NULL
title VARCHAR(255) NOT NULL
description TEXT
difficulty VARCHAR(30)
passing_score NUMERIC(5,2) NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign key:

```text
skill_id
    → skills.id
```

Constraints:

```text
passing_score >= 0
passing_score <= 100
```

---

# 17. Table: assessment_questions

Stores individual questions.

```text
assessment_questions
--------------------
id UUID PRIMARY KEY
assessment_id UUID NOT NULL
question TEXT NOT NULL
question_type VARCHAR(40) NOT NULL
options JSONB
correct_answer TEXT NOT NULL
explanation TEXT
points NUMERIC(8,2) NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign key:

```text
assessment_id
    → assessments.id
```

Critical security rule:

`correct_answer` must NEVER be returned to the frontend before assessment submission.

The backend owns answer validation.

---

# 18. Table: assessment_results

Stores learner assessment attempts.

```text
assessment_results
------------------
id UUID PRIMARY KEY
assessment_id UUID NOT NULL
learner_id UUID NOT NULL
score NUMERIC(5,2) NOT NULL
skill_mastery NUMERIC(5,2) NOT NULL
attempt_number INTEGER NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
assessment_id
    → assessments.id

learner_id
    → learner_profiles.id
```

Constraints:

```text
score >= 0
score <= 100

skill_mastery >= 0
skill_mastery <= 100

attempt_number >= 1
```

Assessment submission should be transactional.

---

# 19. Table: roadmaps

Represents a generated learning roadmap.

```text
roadmaps
--------
id UUID PRIMARY KEY
learner_id UUID NOT NULL
target_role_id UUID NOT NULL
version INTEGER NOT NULL
status VARCHAR(30) NOT NULL
estimated_weeks INTEGER
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
learner_id
    → learner_profiles.id

target_role_id
    → roles.id
```

Possible statuses:

```text
draft
active
completed
superseded
archived
```

Only one roadmap version should normally be active for a learner.

---

# 20. Table: roadmap_items

Represents individual roadmap milestones/actions.

```text
roadmap_items
-------------
id UUID PRIMARY KEY
roadmap_id UUID NOT NULL
skill_id UUID
resource_id UUID
project_id UUID
assessment_id UUID
sequence INTEGER NOT NULL
status VARCHAR(30) NOT NULL
progress NUMERIC(5,2) NOT NULL DEFAULT 0
estimated_hours NUMERIC(8,2)
reason JSONB
locked_reason TEXT
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
roadmap_id
    → roadmaps.id

skill_id
    → skills.id

resource_id
    → resources.id

project_id
    → projects.id

assessment_id
    → assessments.id
```

Possible statuses:

```text
LOCKED
AVAILABLE
IN_PROGRESS
COMPLETED
NEEDS_REVIEW
```

State transitions must be validated by application/domain logic.

Valid transitions:

```text
LOCKED → AVAILABLE
AVAILABLE → IN_PROGRESS
IN_PROGRESS → COMPLETED
COMPLETED → NEEDS_REVIEW
NEEDS_REVIEW → IN_PROGRESS
```

A roadmap item must not recommend an inaccessible or invalid resource.

---

# 21. Table: recommendations

Stores recommendation decisions for explainability and debugging.

```text
recommendations
---------------
id UUID PRIMARY KEY
learner_id UUID NOT NULL
skill_id UUID
resource_id UUID
score NUMERIC(8,6) NOT NULL
ranking INTEGER
reason JSONB NOT NULL
algorithm_version VARCHAR(50)
created_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
learner_id
    → learner_profiles.id

skill_id
    → skills.id

resource_id
    → resources.id
```

Example `reason`:

```json
{
  "skill_gap": 0.68,
  "goal_relevance": 0.92,
  "prerequisite_fit": 1.0,
  "difficulty_fit": 0.88,
  "time_fit": 0.91,
  "preference_fit": 0.80
}
```

The recommendation explanation shown to users must be generated from these actual structured factors.

The LLM must not invent recommendation reasons.

---

# 22. Table: feedback

Stores learner feedback.

```text
feedback
--------
id UUID PRIMARY KEY
learner_id UUID NOT NULL
resource_id UUID
feedback_type VARCHAR(50) NOT NULL
rating INTEGER
comment TEXT
created_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
learner_id
    → learner_profiles.id

resource_id
    → resources.id
```

Possible feedback types:

```text
helpful
not_helpful
not_relevant
too_easy
too_difficult
completed
skipped
```

Rating:

```text
1–5
```

---

# 23. Table: progress

Stores actual learner activity against roadmap items.

```text
progress
--------
id UUID PRIMARY KEY
learner_id UUID NOT NULL
roadmap_item_id UUID NOT NULL
status VARCHAR(30) NOT NULL
percentage NUMERIC(5,2) NOT NULL DEFAULT 0
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
time_spent_minutes INTEGER NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign keys:

```text
learner_id
    → learner_profiles.id

roadmap_item_id
    → roadmap_items.id
```

Constraints:

```text
percentage >= 0
percentage <= 100

time_spent_minutes >= 0
```

Progress must come from actual learner activity.

Do not create fake dashboard percentages.

---

# 24. Table: conversations

Stores AI Assistant conversations.

```text
conversations
-------------
id UUID PRIMARY KEY
learner_id UUID NOT NULL
title VARCHAR(255)
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Foreign key:

```text
learner_id
    → learner_profiles.id
```

The conversation belongs to exactly one learner.

---

# 25. Table: conversation_messages

Stores individual AI assistant messages.

```text
conversation_messages
---------------------
id UUID PRIMARY KEY
conversation_id UUID NOT NULL
role VARCHAR(30) NOT NULL
content TEXT NOT NULL
metadata JSONB NOT NULL DEFAULT '{}'
created_at TIMESTAMPTZ NOT NULL
```

Foreign key:

```text
conversation_id
    → conversations.id
```

Allowed roles:

```text
user
assistant
system
```

Do not expose internal system prompts to the learner.

The assistant context must be dynamically constructed from relevant learner state.

Do not send the entire database to the LLM.

---

# 26. Table: roadmap_versions

Roadmap versions must preserve important historical state.

```text
roadmap_versions
----------------
id UUID PRIMARY KEY
roadmap_id UUID NOT NULL
version INTEGER NOT NULL
trigger_type VARCHAR(50) NOT NULL
reason JSONB
created_at TIMESTAMPTZ NOT NULL
```

Foreign key:

```text
roadmap_id
    → roadmaps.id
```

Possible trigger types:

```text
initial_generation
assessment
feedback
profile_change
study_time_change
goal_change
manual_regeneration
adaptive_update
```

Example:

```text
Roadmap v1
    ↓
Assessment
    ↓
Weakness detected
    ↓
Adaptive Update
    ↓
Roadmap v2
```

Historical roadmap state must not be destroyed unnecessarily.

---

# 27. Foreign Key Summary

Implement these relationships:

```text
learner_profiles.user_id
    → users.id

learner_profiles.target_role_id
    → roles.id

role_skills.role_id
    → roles.id

role_skills.skill_id
    → skills.id

learner_skills.learner_id
    → learner_profiles.id

learner_skills.skill_id
    → skills.id

skill_prerequisites.skill_id
    → skills.id

skill_prerequisites.prerequisite_skill_id
    → skills.id

resource_skills.resource_id
    → resources.id

resource_skills.skill_id
    → skills.id

project_skills.project_id
    → projects.id

project_skills.skill_id
    → skills.id

assessments.skill_id
    → skills.id

assessment_questions.assessment_id
    → assessments.id

assessment_results.assessment_id
    → assessments.id

assessment_results.learner_id
    → learner_profiles.id

roadmaps.learner_id
    → learner_profiles.id

roadmaps.target_role_id
    → roles.id

roadmap_items.roadmap_id
    → roadmaps.id

roadmap_items.skill_id
    → skills.id

roadmap_items.resource_id
    → resources.id

roadmap_items.project_id
    → projects.id

roadmap_items.assessment_id
    → assessments.id

recommendations.learner_id
    → learner_profiles.id

recommendations.skill_id
    → skills.id

recommendations.resource_id
    → resources.id

feedback.learner_id
    → learner_profiles.id

feedback.resource_id
    → resources.id

progress.learner_id
    → learner_profiles.id

progress.roadmap_item_id
    → roadmap_items.id

conversations.learner_id
    → learner_profiles.id

conversation_messages.conversation_id
    → conversations.id

roadmap_versions.roadmap_id
    → roadmaps.id
```

---

# 28. Index Strategy

At minimum create indexes for:

```text
users.email

learner_skills.learner_id
learner_skills.skill_id

role_skills.role_id
role_skills.skill_id

skill_prerequisites.skill_id
skill_prerequisites.prerequisite_skill_id

resource_skills.resource_id
resource_skills.skill_id

project_skills.project_id
project_skills.skill_id

roadmaps.learner_id
roadmaps.target_role_id

roadmap_items.roadmap_id
roadmap_items.sequence

assessment_results.learner_id
assessment_results.assessment_id

recommendations.learner_id

feedback.learner_id

progress.learner_id
progress.roadmap_item_id

conversations.learner_id
conversation_messages.conversation_id

roadmap_versions.roadmap_id
```

For vector search, create the appropriate pgvector index after the embedding dimension and similarity strategy are finalized.

Do not add unnecessary indexes blindly.

Indexes must reflect actual query patterns.

---

# 29. Unique Constraints

Required unique constraints:

```text
users.email

learner_profiles.user_id

skills.name
skills.slug

roles.name
roles.slug

role_skills(role_id, skill_id)

learner_skills(learner_id, skill_id)

skill_prerequisites(skill_id, prerequisite_skill_id)

resource_skills(resource_id, skill_id)

project_skills(project_id, skill_id)

roadmaps(learner_id, version)

roadmap_items(roadmap_id, sequence)

assessment_results(assessment_id, learner_id, attempt_number)

roadmap_versions(roadmap_id, version)
```

---

# 30. Delete Behavior

Do not cascade-delete important historical learner data accidentally.

Recommended policy:

### User deletion

Prefer soft deactivation:

```text
is_active = false
```

rather than immediate destructive deletion.

### Reference data

For:

```text
skills
roles
resources
projects
assessments
```

prefer deactivation/archive behavior where practical.

### Historical data

Do not delete:

```text
assessment_results
progress
recommendations
roadmap_versions
conversation history
```

merely because a new roadmap is generated.

---

# 31. Roadmap Version Rules

A learner may have:

```text
v1
v2
v3
...
```

Only the appropriate current version should be marked:

```text
active
```

When adaptation occurs:

```text
DO NOT overwrite v1

CREATE v2

mark v1 as superseded
mark v2 as active
```

Historical state should remain queryable.

---

# 32. Skill Gap Data

Do not create a permanent `skill_gaps` table for the initial MVP unless a concrete query/use case requires persistent snapshots.

Skill gap can be calculated from:

```text
role_skills
+
learner_skills
```

Formula:

```text
gap =
required_proficiency - learner_proficiency
```

Clamp minimum value to zero.

Example:

```text
Required = 80
Current = 35

Gap = 45
```

Priority can use:

```text
Gap
×
Importance
×
DependencyImpact
```

The implementation must keep the formula configurable.

---

# 33. Recommendation Data

Recommendation scoring should remain deterministic.

Initial score:

```text
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
```

All components must be normalized.

Weights must be configurable.

The resulting score and contributing factors should be persisted in:

```text
recommendations
```

This provides explainability and debugging.

---

# 34. Vector / Embedding Storage

Resources and projects may contain embeddings.

Embedding text should be constructed from meaningful content.

For a resource:

```text
Title
Description
Skills
Prerequisites
Learning Outcomes
```

Do not embed only the title.

Store:

```text
embedding
```

alongside the original relational record.

Semantic retrieval flow:

```text
User Query
    ↓
Query Embedding
    ↓
pgvector similarity
    ↓
Candidate Resources
    ↓
Metadata Filtering
    ↓
Hybrid Ranking
    ↓
Final Recommendation
```

Semantic similarity must not bypass:

```text
skill relevance
difficulty
prerequisites
role relevance
availability
time fit
preferences
```

---

# 35. Transaction Requirements

Use database transactions for operations that must remain atomic.

Critical example:

```text
Submit Assessment
      ↓
Save Assessment Result
      ↓
Update Learner Skill Mastery
      ↓
Detect Weak Skill
      ↓
Trigger Adaptive Logic
      ↓
Create New Roadmap Version
      ↓
Update Roadmap State
```

If a required step fails, the transaction must not leave the database in an inconsistent state.

---

# 36. Concurrency

Prevent duplicate roadmap generation caused by simultaneous requests.

Use appropriate mechanisms:

```text
idempotency
status checks
database locking where necessary
```

Example:

If two identical roadmap-generation requests arrive simultaneously, the backend must not blindly create two active roadmaps.

---

# 37. Alembic Migrations

All schema changes must be managed through Alembic.

Required workflow:

```text
Model Change
    ↓
Alembic Migration
    ↓
Review Migration
    ↓
Apply Migration
```

Never manually alter the production schema without migration tracking.

Suggested commands:

```bash
alembic revision --autogenerate -m "create initial database schema"

alembic upgrade head
```

The exact command configuration may vary with the project setup.

---

# 38. Seed Database

Create:

```text
scripts/seed_database.py
```

Seed data must include at minimum:

```text
roles
skills
skill prerequisites
role-skill relationships
resources
resource-skill relationships
projects
project-skill relationships
assessments
assessment questions
```

The seed process must be:

```text
repeatable
```

and preferably:

```text
idempotent
```

Do not duplicate records every time the seed script runs.

---

# 39. Initial Seed Content

The demo must contain enough structured data to demonstrate the complete intelligence pipeline.

At minimum provide:

```text
6–8 roles

30+ skills

meaningful prerequisite relationships

role-skill mappings

50+ trusted resources

10+ projects

multiple assessments

assessment questions
```

These numbers are implementation targets for a convincing prototype, not fake user metrics.

Do not fabricate external resources.

Every resource must contain a valid trusted URL or clearly be marked as internal/demo content.

---

# 40. Database Initialization Order

The recommended initialization order is:

```text
1. PostgreSQL
        ↓
2. Extensions
        ↓
3. Alembic migrations
        ↓
4. Roles
        ↓
5. Skills
        ↓
6. Skill prerequisites
        ↓
7. Role-skill relationships
        ↓
8. Resources
        ↓
9. Resource-skill relationships
        ↓
10. Projects
        ↓
11. Project-skill relationships
        ↓
12. Assessments
        ↓
13. Assessment questions
```

---

# 41. SQLAlchemy Requirements

Use SQLAlchemy models corresponding to the database entities.

Recommended organization:

```text
backend/app/models/

user.py
learner_profile.py
skill.py
role.py
role_skill.py
learner_skill.py
skill_prerequisite.py
resource.py
resource_skill.py
project.py
project_skill.py
assessment.py
assessment_question.py
assessment_result.py
roadmap.py
roadmap_item.py
recommendation.py
feedback.py
progress.py
conversation.py
conversation_message.py
roadmap_version.py
```

Avoid putting every model into one extremely large file.

---

# 42. Repository Layer

Database access must happen through repositories/services rather than directly inside API route handlers.

Example:

```text
API
 ↓
Service
 ↓
Repository
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

Do not write complex database queries directly inside FastAPI route handlers.

---

# 43. Data Integrity Rules

The backend must enforce:

```text
No orphaned foreign keys
No duplicate learner skills
No duplicate role-skill mappings
No duplicate resource-skill mappings
No duplicate project-skill mappings
No invalid proficiency values
No invalid scores
No invalid progress percentages
No self-prerequisites
No invalid roadmap state transitions
No duplicate roadmap versions
No duplicate assessment attempts
```

---

# 44. Security Rules

Never expose:

```text
password_hash
correct_answer
internal prompts
API keys
database credentials
JWT secrets
internal infrastructure details
```

Authentication and authorization must be enforced at the backend.

A learner must only access:

```text
their own profile
their own skills
their own roadmap
their own progress
their own assessments/results
their own feedback
their own conversations
```

Reference data such as:

```text
skills
roles
resources
projects
```

may be shared according to application permissions.

---

# 45. AI Source-of-Truth Rules

The database is authoritative for:

```text
learner progress
assessment scores
completed learning
prerequisites
resource records
resource URLs
permissions
```

The LLM may:

```text
interpret
explain
summarize
converse
```

The LLM must not overwrite authoritative database facts without validated application logic.

---

# 46. Database-to-AI Context

The AI assistant must receive only relevant context.

Example:

```text
Learner:
AI/ML Engineer

Skills:
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
```

Do not send the entire database to the LLM.

---

# 47. Dashboard Data Rule

Dashboard values must be derived from actual database state.

Examples:

```text
overall progress
completed milestones
current milestone
skill growth
assessment performance
weak skills
next best action
```

Do not hardcode:

```text
34% progress
7 completed courses
12 hours learned
```

unless those values are genuinely represented by the underlying demo learner activity.

---

# 48. Database Health

Implement:

```http
GET /health
```

The endpoint should return:

```json
{
  "status": "ok"
}
```

A more advanced implementation may check database connectivity without exposing sensitive infrastructure information.

---

# 49. Development Environment

Recommended local architecture:

```text
frontend
backend
postgres
```

PostgreSQL should be reproducible through Docker where practical.

Local setup:

```text
Clone repository
    ↓
Install dependencies
    ↓
Configure .env
    ↓
Start PostgreSQL
    ↓
Run migrations
    ↓
Seed database
    ↓
Start backend
    ↓
Start frontend
```

---

# 50. Environment Variables

Use:

```text
DATABASE_URL=
JWT_SECRET=
LLM_API_KEY=
EMBEDDING_API_KEY=
CORS_ORIGINS=
ENVIRONMENT=
```

Never commit:

```text
.env
```

Commit:

```text
.env.example
```

---

# 51. Database Definition of Done

The database implementation is complete only when:

```text
[ ] PostgreSQL starts successfully
[ ] pgvector is enabled
[ ] Alembic migrations run successfully
[ ] All required tables exist
[ ] Foreign keys are enforced
[ ] Unique constraints are enforced
[ ] Required indexes exist
[ ] Seed script works
[ ] Seed script is repeatable/idempotent
[ ] Roles are seeded
[ ] Skills are seeded
[ ] Prerequisites are seeded
[ ] Role-skill mappings are seeded
[ ] Resources are seeded
[ ] Resource-skill mappings are seeded
[ ] Projects are seeded
[ ] Project-skill mappings are seeded
[ ] Assessments are seeded
[ ] Assessment questions are seeded
[ ] Vector embeddings can be stored
[ ] Vector retrieval can be executed
[ ] Learner profile can be persisted
[ ] Learner skills can be persisted
[ ] Roadmap can be persisted
[ ] Roadmap versions can be persisted
[ ] Progress can be persisted
[ ] Assessment results can be persisted
[ ] Recommendations can be persisted
[ ] Feedback can be persisted
[ ] Conversations can be persisted
[ ] Conversation messages can be persisted
[ ] Transaction boundaries are implemented
[ ] Unauthorized learner data access is prevented
[ ] No sensitive fields are exposed
[ ] Database health check works
```

---

# 52. Final Database Architecture

The final database architecture should be:

```text
                    PostgreSQL
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Identity        Knowledge         Learning
        │                │                │
        ▼                ▼                ▼
     users             skills          roadmaps
        │                │                │
        ▼                ├── roles       ├── roadmap_items
learner_profiles         │                │
        │                ├── prerequisites│
        ├── learner_skills                ├── progress
        │                │                │
        │                ├── resources    └── versions
        │                │
        │                ├── projects
        │                │
        │                └── assessments
        │
        ├── recommendations
        ├── feedback
        └── conversations
                  │
                  └── conversation_messages

                    + pgvector
                         │
                         ▼
               Semantic Resource Search
```

The database must support the complete PathFinder intelligence loop:

```text
Learner
   ↓
Goal
   ↓
Profile
   ↓
Skills
   ↓
Skill Gap
   ↓
Prerequisite Graph
   ↓
Recommendations
   ↓
Roadmap
   ↓
Learning
   ↓
Assessment
   ↓
Mastery
   ↓
Adaptation
   ↓
New Roadmap Version
```

This database is an implementation foundation for the existing PathFinder product, technical and AI specifications. Do not redesign the product behavior while implementing the schema.