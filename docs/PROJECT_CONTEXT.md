# PathFinder AI — Project Context

**Document:** PROJECT_CONTEXT.md
**Version:** 1.0
**Project:** PathFinder AI
**Project Type:** AI-Powered Personalized Learning Path Recommender
**Competition:** Round 2 — PathFinder Prototype
**Organization:** Technocrats Group of Institutions
**Team:** INVINCIBLE
**Development Stage:** Prototype / MVP
**Submission Deadline:** 31 August 2026, 11:59 PM IST

---

# 1. IMPORTANT INSTRUCTION TO THE AI AGENT

You are the primary software engineering agent responsible for helping build **PathFinder AI**.

This is not a classroom CRUD project.

This project is being developed as a **professional, company-quality AI product prototype** for evaluation in a competitive technical project environment.

The final application must look and behave like a real modern SaaS product.

Do not create:

* a generic college dashboard
* a static course-list application
* a fake AI chatbot
* a collection of disconnected pages
* hardcoded recommendations presented as AI intelligence
* UI-only features without backend logic
* placeholder functionality marked as complete
* fake metrics that imply real user activity
* invented course information or URLs

Every important feature must have a real underlying implementation appropriate for an MVP.

When a feature cannot be fully implemented because of an external dependency, clearly identify the limitation and implement the best reliable fallback rather than silently creating fake functionality.

---

# 2. PRODUCT NAME

## PathFinder AI

### Product tagline

> From where you are to where you want to be — one intelligent learning path.

---

# 3. PRODUCT CATEGORY

PathFinder AI is an:

* AI-powered learning assistant
* personalized recommendation platform
* skill-gap analysis system
* adaptive learning roadmap generator
* educational decision-support system

It combines deterministic software logic with AI capabilities.

---

# 4. CORE PRODUCT IDEA

PathFinder is designed around a simple problem:

> Learners have access to thousands of educational resources, but they often do not know what to learn first, what prerequisites they are missing, which resources are appropriate for their level, or how their learning path should change when their performance changes.

PathFinder solves this by converting a learner's goal into a structured and adaptive learning journey.

The system should determine:

1. Where the learner currently is.
2. Where the learner wants to go.
3. Which skills are required.
4. Which skills are missing.
5. Which prerequisites must be completed.
6. Which resources are appropriate.
7. What should be learned next.
8. Why the recommendation was made.
9. Whether the learner is progressing correctly.
10. Whether the roadmap should change.

---

# 5. PRODUCT VISION

PathFinder should function as an intelligent navigation system for learning.

A learner should not need to manually research:

* which skills are required for a career
* which course to take first
* which prerequisite is missing
* which project to build
* which assessment to attempt
* what to do after failing an assessment

PathFinder should provide this intelligence through one unified experience.

---

# 6. PRODUCT MISSION

The mission of PathFinder is:

> To transform unstructured learning and career goals into personalized, prerequisite-aware, explainable and continuously adaptive learning paths.

---

# 7. THE CORE DIFFERENTIATOR

PathFinder is NOT primarily a course recommendation engine.

It is a **learning-path intelligence engine**.

Traditional recommendation:

```text
User wants Data Science
        ↓
Recommend:
Course A
Course B
Course C
Course D
```

PathFinder:

```text
User wants Data Science
        ↓
Understand learner
        ↓
Identify target competencies
        ↓
Analyze current skills
        ↓
Calculate skill gaps
        ↓
Understand prerequisites
        ↓
Build dependency graph
        ↓
Rank learning resources
        ↓
Generate ordered roadmap
        ↓
Explain recommendations
        ↓
Assess learner
        ↓
Adapt roadmap
```

This distinction must be visible throughout the application.

---

# 8. TARGET USERS

## 8.1 Students

Students who want to:

* prepare for placements
* learn a new technical domain
* transition into AI/ML
* become developers
* prepare for cloud careers
* build project portfolios
* identify skill gaps

## 8.2 Early-Career Professionals

Professionals who want to:

* upskill
* reskill
* change technology stacks
* transition to another role
* prepare for certifications

## 8.3 Self-Learners

Users who want:

* structure
* personalized guidance
* learning roadmaps
* progress tracking
* project recommendations
* continuous feedback

---

# 9. PRIMARY PERSONA

The main demo persona should be a technical student.

Example:

```text
Name:
Demo User

Education:
B.Tech Computer Science

Current Level:
Intermediate

Goal:
Become an AI/ML Engineer

Existing Skills:
Python
SQL
Basic Machine Learning

Study Time:
2 hours/day

Target Duration:
6 months
```

This persona should be used for the primary demonstration flow.

---

# 10. PRIMARY USER JOURNEY

The primary user journey is:

```text
Landing Page
      ↓
Create Learning Profile
      ↓
Describe Goal in Natural Language
      ↓
AI Goal Analysis
      ↓
Current Skill Assessment
      ↓
Skill Gap Analysis
      ↓
Personalized Roadmap
      ↓
Explore Recommendations
      ↓
Learn
      ↓
Assessment
      ↓
Progress Update
      ↓
Adaptive Roadmap
      ↓
Next Best Action
```

Every major feature should support this journey.

---

# 11. PRIMARY DEMO JOURNEY

The final hackathon demo should follow one coherent story.

## Step 1 — User Goal

The user says:

> I want to become an AI/ML Engineer in six months. I know Python and basic SQL, and I can study two hours every day.

## Step 2 — AI Understanding

PathFinder extracts:

```text
Target Role:
AI/ML Engineer

Timeline:
6 months

Study Availability:
2 hours/day

Existing Skills:
Python
SQL

Experience:
Intermediate
```

## Step 3 — Skill Gap

PathFinder identifies:

```text
Python              Strong
SQL                 Moderate
Statistics          Weak
Machine Learning    Weak
Deep Learning       Very Weak
MLOps               Missing
```

## Step 4 — Roadmap

PathFinder creates:

```text
Python for ML
      ↓
Statistics & Probability
      ↓
Data Processing
      ↓
Machine Learning
      ↓
Model Evaluation
      ↓
Deep Learning
      ↓
Generative AI
      ↓
MLOps
      ↓
Capstone Project
```

## Step 5 — Explanation

The user asks:

> Why do I need statistics before machine learning?

PathFinder answers using the learner's actual profile and roadmap.

## Step 6 — Assessment

The learner performs poorly in Model Evaluation.

## Step 7 — Adaptation

PathFinder detects the weakness and modifies the roadmap.

Example:

```text
Original:
Machine Learning
      ↓
Deep Learning

Updated:
Machine Learning
      ↓
Model Evaluation Refresher
      ↓
Practice Assessment
      ↓
Model Comparison Project
      ↓
Deep Learning
```

## Step 8 — Dashboard

The dashboard displays:

* progress
* skill growth
* milestones
* weak areas
* next recommended action

This should be the central demonstration of PathFinder's intelligence.

---

# 12. REQUIRED PRODUCT CAPABILITIES

The MVP must contain the following capabilities.

## Capability 1 — Conversational Onboarding

Users can describe goals using natural language.

## Capability 2 — Learner Profiling

The system stores:

* goals
* experience
* skills
* proficiency
* learning history
* study time
* preferences

## Capability 3 — Skill Gap Detection

The system compares current skills with target-role requirements.

## Capability 4 — Skill Dependency Understanding

The system knows which skills require other skills first.

## Capability 5 — Resource Recommendation

The system recommends appropriate learning resources.

## Capability 6 — Personalized Roadmap

The system generates ordered milestones.

## Capability 7 — Recommendation Explanation

The system explains why each recommendation exists.

## Capability 8 — Assessment

Users can evaluate their understanding.

## Capability 9 — Progress Tracking

The system tracks learning progress.

## Capability 10 — Adaptive Learning

Assessment results and feedback can modify the roadmap.

## Capability 11 — Context-Aware AI Assistant

The assistant understands the user's current learning state.

## Capability 12 — Dashboard

The user can see overall learning status.

---

# 13. WHAT PATHFINDER SHOULD NOT BECOME

Avoid unnecessary product expansion.

Do not prioritize:

* social networking
* messaging between learners
* complex instructor management
* marketplace functionality
* payment systems
* full LMS functionality
* video hosting
* live classes
* complicated enterprise administration
* native mobile application
* unnecessary microservices

The project is evaluated primarily on the intelligent learning-path problem.

---

# 14. PRODUCT EXPERIENCE PRINCIPLES

The application should feel:

### Intelligent

The system should appear to understand the learner's actual situation.

### Personalized

Different users with different profiles should receive different paths.

### Explainable

Users should understand why recommendations were made.

### Adaptive

The roadmap should change when learner state changes.

### Practical

Recommendations should lead to actionable learning.

### Professional

The UI should resemble a modern SaaS product.

### Trustworthy

The application should distinguish known information from generated information.

---

# 15. PERSONALIZATION PRINCIPLE

Personalization must affect actual recommendations.

For example:

### User A

```text
Python: 90%
Statistics: 80%
ML: 20%
```

Should receive a different path from:

### User B

```text
Python: 30%
Statistics: 20%
ML: 5%
```

The application must not simply generate the same roadmap for everyone.

---

# 16. ADAPTATION PRINCIPLE

A roadmap generated once is not sufficient.

The system must support:

```text
Initial learner state
        ↓
Learning
        ↓
Assessment
        ↓
New learner state
        ↓
Recommendation recalculation
        ↓
Updated roadmap
```

The adaptation should be visible to the user.

---

# 17. EXPLAINABILITY PRINCIPLE

Every major recommendation should be explainable.

Example:

```text
Why is this recommended?

Skill gap:
68%

Prerequisites:
Satisfied

Goal relevance:
High

Difficulty:
Matches your level

Time fit:
Fits your weekly study capacity
```

The explanation must be based on actual recommendation inputs.

Do not fabricate explanations after generating a recommendation.

---

# 18. AI PRINCIPLE

AI should be used where it adds meaningful value.

Appropriate AI use:

* natural-language goal understanding
* learner intent extraction
* semantic resource retrieval
* conversational tutoring
* personalized explanations
* roadmap reasoning assistance
* natural-language feedback

Deterministic software should be used where predictable behavior is better:

* progress calculation
* score calculation
* prerequisite validation
* permissions
* database operations
* completion status
* recommendation scoring
* roadmap state transitions

Do not use an LLM for basic calculations that can be performed deterministically.

---

# 19. SOURCE-OF-TRUTH PRINCIPLE

The LLM is not the source of truth for:

* learner progress
* assessment scores
* completed courses
* prerequisite relationships
* database records
* resource URLs
* authorization
* system permissions

Structured application data is the source of truth.

The LLM may interpret and explain this data.

---

# 20. RESOURCE INTEGRITY PRINCIPLE

The AI must not invent educational resources.

If a resource is not present in the trusted resource dataset or verified retrieval source, the system should not present it as a verified recommendation.

Resource records should contain structured metadata.

---

# 21. TRUST PRINCIPLE

The application should clearly distinguish:

```text
Verified Data
AI Interpretation
AI Suggestion
User-Provided Information
```

Avoid presenting uncertain AI-generated information as factual system data.

---

# 22. MVP CAREER PATHS

The prototype should initially support approximately 6–8 career paths.

Recommended paths:

1. AI/ML Engineer
2. Data Scientist
3. Data Analyst
4. Full Stack Developer
5. Backend Developer
6. Cloud Engineer
7. DevOps Engineer
8. Cybersecurity Analyst

The architecture must allow additional roles to be added through data rather than requiring major code changes.

---

# 23. MVP SKILL DATA

The prototype should contain a structured skill catalog.

Target initial size:

```text
50–100 skills
100–200 learning resources
30–50 projects
100+ assessment questions
```

The exact quantity can change based on development time.

Quality and relationships are more important than dataset size.

---

# 24. SKILL DATA MODEL

Each skill should conceptually contain:

```text
Skill ID
Name
Category
Description
Difficulty
Estimated Learning Hours
Prerequisites
Related Skills
Target Roles
Assessment
Projects
```

Example:

```text
Skill:
Model Evaluation

Category:
Machine Learning

Difficulty:
Intermediate

Prerequisites:
Regression
Classification
Basic Statistics

Estimated Hours:
6

Target Roles:
Data Scientist
ML Engineer
```

---

# 25. RESOURCE DATA MODEL

Each learning resource should contain:

```text
Resource ID
Title
Description
Type
Provider
URL
Difficulty
Duration
Skills
Prerequisites
Quality Metadata
```

Possible resource types:

* course
* tutorial
* documentation
* article
* video
* project
* exercise
* assessment

---

# 26. PROJECT DATA MODEL

Projects should be connected to skills.

Example:

```text
Project:
Customer Churn Prediction

Required Skills:
Python
Pandas
Classification
Feature Engineering
Model Evaluation

Difficulty:
Intermediate

Estimated Time:
8 hours
```

---

# 27. ASSESSMENT MODEL

Assessments should be associated with specific skills.

Assessment types:

* MCQ
* conceptual
* coding
* scenario-based
* practical

Assessment results should update learner state.

---

# 28. DASHBOARD PURPOSE

The dashboard is not just for displaying charts.

Its main purpose is to answer:

> What have I achieved, where am I weak, and what should I do next?

The most prominent dashboard element should therefore be:

## NEXT BEST ACTION

Example:

```text
Recommended Next Action

Complete:
Model Evaluation Refresher

Estimated Time:
45 minutes

Reason:
Your latest assessment indicates
a weakness in model evaluation.

[Continue Learning]
```

---

# 29. ROADMAP PURPOSE

The roadmap should communicate:

* sequence
* prerequisites
* progress
* milestones
* expected outcomes
* recommended resources
* projects
* assessments

The roadmap should visually distinguish:

```text
Completed
In Progress
Available
Locked
Needs Review
```

---

# 30. LOCKED CONTENT PRINCIPLE

A learner should not necessarily be able to start every advanced milestone immediately.

If prerequisites are incomplete:

```text
Machine Learning
LOCKED

Required:
✓ Python
✗ Statistics
✗ Probability
```

The system should explain how to unlock it.

---

# 31. FEEDBACK LOOP

Users should be able to provide feedback.

Examples:

```text
Helpful
Not Helpful
Too Easy
Too Difficult
Too Long
Already Know This
Not Relevant
```

This feedback may influence future recommendations.

---

# 32. LEARNING PREFERENCES

The profile may include:

* video preference
* text preference
* project-based preference
* hands-on preference
* theory preference
* short sessions
* long sessions

These preferences should influence resource ranking.

---

# 33. TIME-AWARE PERSONALIZATION

The roadmap should consider available learning time.

Example:

```text
Learner A:
1 hour/day

Learner B:
4 hours/day
```

They should not receive identical timelines.

The system should estimate:

```text
Available Hours
+
Estimated Skill Hours
=
Approximate Learning Timeline
```

---

# 34. TIMELINE PRINCIPLE

Timelines are estimates, not guarantees.

Do not claim:

> "You will definitely become an AI Engineer in 6 months."

Instead:

> "Based on your current profile and available study time, this roadmap is estimated to take approximately six months."

---

# 35. USER EXPERIENCE STATES

Every major UI feature must support:

### Loading State

Clearly indicate that data is being processed.

### Empty State

Explain what the user needs to do.

### Error State

Provide a useful recovery action.

### Success State

Confirm what happened.

### Partial State

Handle incomplete data gracefully.

### Offline/External Failure

Provide fallback behavior where possible.

---

# 36. PROFESSIONAL UI EXPECTATION

The UI should have:

* consistent spacing
* strong typography
* clear hierarchy
* accessible contrast
* responsive layout
* subtle animations
* useful empty states
* clear CTA hierarchy
* meaningful icons
* consistent component system

Avoid:

* excessive gradients
* random colors
* excessive animations
* cluttered cards
* meaningless statistics
* oversized headings everywhere
* template-like college-project appearance

---

# 37. BRAND PERSONALITY

PathFinder should feel:

```text
Modern
Intelligent
Focused
Trustworthy
Technical
Helpful
Premium
```

It should not feel:

```text
Childish
Game-like by default
Overly academic
Generic
AI-generated
```

---

# 38. ACCESSIBILITY

The product should consider:

* keyboard navigation
* readable typography
* semantic HTML
* accessible form labels
* sufficient color contrast
* meaningful error messages
* accessible buttons
* focus states

Accessibility should be considered during frontend development rather than added at the end.

---

# 39. SECURITY CONTEXT

Security is part of product quality.

At minimum, consider:

* authentication
* authorization
* input validation
* secure password storage
* environment secrets
* API protection
* rate limiting
* CORS
* XSS prevention
* SQL injection prevention
* secure error responses
* prompt injection protection

Never expose secrets in frontend code or Git.

---

# 40. PRIVACY CONTEXT

Learner data may include:

* career goals
* learning history
* assessment results
* skills
* preferences

Only required data should be stored.

Do not expose one learner's information to another learner.

---

# 41. FAILURE PHILOSOPHY

When something fails:

Do not hide the failure.

Do not silently generate fake data.

Do not mark the operation successful.

Instead:

1. Detect failure.
2. Log useful technical information securely.
3. Show a user-friendly message.
4. Provide a fallback if available.
5. Allow retry where appropriate.

---

# 42. DEMO RELIABILITY

The demo must be deterministic enough to work reliably.

A curated demo dataset is acceptable.

However, the application must still demonstrate genuine underlying functionality.

For example:

Acceptable:

```text
Curated skill dataset
+
Real recommendation engine
+
Real assessment
+
Real adaptive logic
```

Not acceptable:

```text
Hardcoded screen
"AI generated roadmap"
Static text pretending to be dynamic
```

---

# 43. DEMO STORY

The demo should communicate one central message:

> PathFinder understands the learner, identifies the gap, creates the path, explains the path, and changes the path when the learner changes.

This message should be reflected in the entire application.

---

# 44. COMPETITION JUDGING ALIGNMENT

The competition weighting is:

```text
Problem Understanding & Solution Design    20%
Functionality & Feature Completeness       25%
AI/ML Implementation                       20%
Innovation & Creativity                    15%
User Experience & Interface                10%
Performance & Code Quality                 10%
```

Development priorities should reflect these weights.

The application must therefore prioritize:

1. Complete core workflow
2. Genuine AI/recommendation implementation
3. Adaptive learning
4. Strong product design
5. Reliable implementation

---

# 45. COMPETITION SUBMISSION REQUIREMENTS

The final project must support preparation of:

## 1. Source Code ZIP

Complete runnable source.

Exclude:

* virtual environments
* build artifacts
* unnecessary dependency folders
* secrets

## 2. GitHub Repository

The repository must:

* be accessible
* contain source code
* contain README
* show meaningful development history

## 3. Solution Documentation

PDF/PPT should cover:

* problem
* solution
* architecture
* AI/ML
* features
* workflows
* challenges
* results

## 4. Demo Video

3–5 minutes.

Must demonstrate:

* core functionality
* workflow
* AI features
* adaptive behavior
* user experience

## 5. Application URL

Provide deployed application URL if available.

Otherwise provide clear local setup instructions.

---

# 46. GITHUB DEVELOPMENT PRINCIPLE

Development history should reflect genuine progress.

Prefer meaningful commits such as:

```text
Initialize project architecture
Implement learner profile
Add skill graph
Implement skill gap engine
Add recommendation scoring
Implement roadmap generation
Add AI assistant
Integrate resource retrieval
Implement assessments
Add adaptive roadmap
Build learner dashboard
Add security validation
Improve responsive UI
Add automated tests
Prepare deployment
```

Avoid one enormous final commit containing the entire project.

---

# 47. DOCUMENTATION PRINCIPLE

The repository should contain documentation explaining:

* project purpose
* architecture
* setup
* environment variables
* database
* API
* AI system
* recommendation engine
* testing
* deployment

A new developer should be able to understand the project without asking the original developer for basic information.

---

# 48. DEVELOPMENT QUALITY BAR

The application should be evaluated as if another engineering team will inherit it.

Therefore:

* code should be modular
* names should be meaningful
* duplicated logic should be minimized
* business logic should not be buried inside UI components
* secrets must not be committed
* API contracts should be explicit
* errors should be handled
* types/schemas should be used where appropriate
* tests should cover important logic
* README must remain accurate

---

# 49. AGENT DECISION PRINCIPLE

When multiple implementation approaches are possible:

Prefer the approach that is:

1. Reliable
2. Simple enough for an MVP
3. Maintainable
4. Explainable
5. Testable
6. Secure
7. Easy to deploy
8. Appropriate for the competition timeline

Do not introduce unnecessary infrastructure simply because it is technically impressive.

---

# 50. NO OVER-ENGINEERING

Avoid unnecessary:

* microservices
* Kubernetes
* event buses
* distributed systems
* complex agent swarms
* custom LLM training
* unnecessary vector databases
* complicated DevOps pipelines

The system should be architecturally sound without becoming unnecessarily complex.

---

# 51. AGENT MUST PRESERVE PRODUCT INTENT

When implementing a feature, always ask:

> Does this feature help PathFinder understand the learner, identify the learning gap, select the next step, explain that decision, or adapt the path?

If the answer is no, the feature is probably outside the MVP.

---

# 52. DEFINITION OF A COMPLETE USER FLOW

A user flow is not complete when the UI exists.

It is complete only when:

```text
UI
 ↓
API
 ↓
Business Logic
 ↓
Database
 ↓
AI / Recommendation Logic where required
 ↓
Response
 ↓
UI Update
 ↓
Error Handling
 ↓
Test
```

All relevant layers must work.

---

# 53. DEFINITION OF DONE

A feature is DONE only when:

* implemented
* integrated
* validated
* tested
* error handled
* responsive where applicable
* documented
* verified through the actual application

Do not mark features complete based only on successful compilation.

---

# 54. FINAL PRODUCT REQUIREMENT

At the end of development, a new user should be able to enter PathFinder and understand the product without external explanation.

The user should immediately understand:

```text
My Goal
   ↓
My Skills
   ↓
My Gaps
   ↓
My Roadmap
   ↓
My Progress
   ↓
My Next Action
```

---

# 55. FINAL PRODUCT STATEMENT

PathFinder should ultimately be described as:

> **An AI-powered adaptive learning navigation platform that converts a learner's career goal into a personalized, prerequisite-aware, explainable and continuously evolving learning path.**

It should not be described merely as:

> "An AI chatbot for course recommendations."

---

# 56. AGENT CONTEXT PRIORITY

When there is a conflict between implementation convenience and product requirements, prioritize in this order:

```text
1. User safety and data security
2. Correctness
3. Product requirements
4. Core user experience
5. Reliability
6. Maintainability
7. Performance
8. Visual polish
9. Optional features
```

Do not sacrifice correctness for visual polish.

Do not sacrifice reliability for unnecessary complexity.

---

# 57. END STATE

The desired end state is a polished working prototype that demonstrates:

```text
Natural Language Goal
        ↓
Learner Profile
        ↓
Skill Gap
        ↓
Skill Graph
        ↓
Hybrid Recommendation
        ↓
Personalized Roadmap
        ↓
Explainable AI
        ↓
Assessment
        ↓
Adaptive Learning
        ↓
Progress Dashboard
```

The entire chain must work as one integrated product.

---

# 58. NEXT SPECIFICATION FILES

This file defines the product context only.

The following specifications must be created before major implementation begins:

```text
PRODUCT_REQUIREMENTS.md
TECHNICAL_SPEC.md
AI_ARCHITECTURE.md
DATABASE_SPEC.md
API_SPEC.md
UI_UX_SPEC.md
AGENT_RULES.md
DEVELOPMENT_PLAN.md
```

Do not assume the details of those files.

They will define the implementation-level requirements separately.

---

# END OF PROJECT_CONTEXT.md
