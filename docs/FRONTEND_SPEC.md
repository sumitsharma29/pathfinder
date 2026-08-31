# PathFinder AI — Frontend Specification

Document: FRONTEND_SPEC.md
Version: 1.0
Status: Implementation Specification
Project: PathFinder AI

==================================================
1. PURPOSE
==================================================

This document defines the frontend architecture,
screens, routes, components, interactions,
responsive behavior and UI requirements for
PathFinder AI.

Frontend must feel like a real modern SaaS product.

It must NOT look like:

- a college project
- a generic admin dashboard
- a static course website
- a template with random cards
- an AI-generated UI with meaningless statistics

PathFinder must communicate:

"I have a goal."
        ↓
"PathFinder understands me."
        ↓
"It identifies what I am missing."
        ↓
"It gives me the correct sequence."
        ↓
"It explains why."
        ↓
"I learn and get assessed."
        ↓
"It adapts my path."
        ↓
"I always know what to do next."


==================================================
2. FRONTEND STACK
==================================================

Use:

React
TypeScript
Vite
Tailwind CSS
Recharts

Recommended supporting libraries:

React Router
TanStack Query
React Hook Form
Zod
Lucide React

Use libraries only when they solve a real problem.

Do not add unnecessary dependencies.


==================================================
3. FRONTEND ARCHITECTURE
==================================================

Use:

Pages
 ↓
Feature Components
 ↓
Hooks
 ↓
API Client
 ↓
Backend API

Do NOT put business logic inside UI components.

Architecture:

src/
  app/
  components/
  features/
  pages/
  layouts/
  hooks/
  services/
  api/
  types/
  utils/
  lib/


==================================================
4. ROUTING
==================================================

Public routes:

/
/login
/register

Onboarding:

/onboarding
/onboarding/goal
/onboarding/profile
/onboarding/skills
/onboarding/review

Application:

/dashboard
/roadmap
/skill-gaps
/resources
/resources/:id
/assessments
/assessments/:id
/assessments/:id/result
/adaptive-update
/assistant
/profile
/settings


==================================================
5. MAIN NAVIGATION
==================================================

Authenticated application navigation:

Dashboard
My Roadmap
Skill Gaps
Resources
Assessments
AI Assistant
Profile
Settings

Desktop:

Persistent sidebar.

Mobile:

Collapsible sidebar / drawer
or bottom navigation where appropriate.

Do not duplicate navigation unnecessarily.


==================================================
6. VISUAL DIRECTION
==================================================

Brand personality:

Modern
Intelligent
Focused
Trustworthy
Technical
Helpful
Premium

Avoid:

- excessive gradients
- random colors
- excessive animation
- cluttered cards
- meaningless statistics
- oversized headings everywhere
- childish UI
- game-like default styling
- generic AI aesthetic
- template-like college-project appearance

Use:

- strong typography hierarchy
- consistent spacing
- restrained color palette
- subtle borders
- meaningful elevation
- clear status indicators
- intentional whitespace


==================================================
7. DESIGN SYSTEM
==================================================

Create reusable design tokens.

Spacing:

Use a consistent spacing scale.

Typography:

Use a clear hierarchy:

Display
H1
H2
H3
Body
Small
Caption

Do not use huge headings on every section.

Radius:

Use consistent border radius across:

- cards
- buttons
- inputs
- modals
- navigation

Shadows:

Use subtle shadows.

Do not make every component heavily elevated.


==================================================
8. COLOR SEMANTICS
==================================================

Colors must communicate meaning.

Primary:

PathFinder brand action.

Success:

Completed / mastered.

Warning:

Needs attention.

Danger:

Error / failed.

Neutral:

Information.

Do not rely only on color.

Every important status should also have:

- text
- icon
- accessible label


==================================================
9. RESPONSIVE DESIGN
==================================================

The application must work on:

Desktop
Tablet
Mobile

At minimum test:

360px
390px
768px
1024px
1280px
1440px

Mobile UI must not simply shrink desktop UI.

Navigation, cards, roadmap and charts must adapt.

No:

- horizontal overflow
- clipped buttons
- inaccessible dialogs
- unreadable charts
- broken roadmap connectors


==================================================
10. SCREEN INVENTORY
==================================================

Required screens:

01 Landing Page
02 Authentication
03 AI Onboarding
04 Learner Profile
05 Skill Gap Analysis
06 Roadmap
07 Resource Detail
08 Assessment
09 Assessment Result
10 Adaptive Update
11 Dashboard
12 AI Assistant
13 Profile / Settings


==================================================
11. SCREEN 01 — LANDING PAGE
==================================================

Route:

/

Purpose:

Introduce PathFinder and communicate the core value.

Hero headline:

"Your Goal. Your Skills. Your Path."

Supporting message:

"PathFinder creates a personalized learning roadmap
based on your goals, skills, progress and learning
preferences."

Primary CTA:

"Build My Learning Path"

Secondary CTA:

"See How It Works"


--------------------------------------------------
11.1 HERO
--------------------------------------------------

Include:

- product logo
- headline
- supporting text
- primary CTA
- secondary CTA
- visual roadmap preview

Visual should demonstrate:

Goal
 ↓
Skills
 ↓
Gap
 ↓
Roadmap
 ↓
Progress


--------------------------------------------------
11.2 HOW IT WORKS
--------------------------------------------------

Show:

01 Tell us your goal
        ↓
02 Analyze your skills
        ↓
03 Identify your gaps
        ↓
04 Build your roadmap
        ↓
05 Learn and adapt


--------------------------------------------------
11.3 FEATURES
--------------------------------------------------

Highlight:

AI Goal Understanding
Skill Gap Analysis
Personalized Roadmaps
Explainable Recommendations
Adaptive Learning
AI Learning Assistant


--------------------------------------------------
11.4 PRODUCT PREVIEW
--------------------------------------------------

Show a realistic roadmap preview.

Demo data is allowed.

Do not display fake product statistics.


--------------------------------------------------
11.5 LANDING ACCEPTANCE
--------------------------------------------------

[ ] loads correctly
[ ] CTA works
[ ] authentication flow works
[ ] mobile works
[ ] no broken links
[ ] no fake statistics
[ ] professional visual quality


==================================================
12. SCREEN 02 — AUTHENTICATION
==================================================

Routes:

/login
/register

Keep authentication simple.

Register fields:

Name
Email
Password
Confirm Password

Login:

Email
Password

Actions:

Login
Create Account

States:

default
loading
success
error

Error messages must be meaningful.

Example:

"Invalid email or password."

Do not expose backend exception messages.


==================================================
13. SCREEN 03 — AI ONBOARDING
==================================================

Routes:

/onboarding
/onboarding/goal
/onboarding/profile
/onboarding/skills
/onboarding/review

This is one of the most important screens.

The onboarding should feel conversational,
not like a boring form.


--------------------------------------------------
13.1 GOAL INPUT
--------------------------------------------------

Headline:

"What do you want to become?"

Input example:

"I want to become a Data Scientist."

Allow natural language.

Primary action:

"Analyze My Goal"


--------------------------------------------------
13.2 AI ANALYSIS
--------------------------------------------------

Show a clear processing state:

Understanding your goal...
Identifying target role...
Analyzing required skills...
Preparing your profile...


Do not use fake progress percentages.

Use real loading state.


--------------------------------------------------
13.3 EXTRACTED PROFILE
--------------------------------------------------

Show:

Target Role
Timeline
Experience
Study Time
Technologies
Existing Skills
Preferences


Example:

Target Role
Data Scientist

Timeline
6 months

Experience
Beginner

Study Time
2 hours/day


Allow user to edit extracted information.

AI output is not final until user confirms it.


--------------------------------------------------
13.4 SKILLS
--------------------------------------------------

Allow learner to:

- add skills
- remove skills
- adjust proficiency
- mark skill confidence

Visual:

Skill
Proficiency
Confidence


--------------------------------------------------
13.5 REVIEW
--------------------------------------------------

Show final summary:

Your Goal
Your Current Skills
Your Experience
Your Availability
Your Learning Preferences

CTA:

"Build My Learning Path"


==================================================
14. SCREEN 04 — LEARNER PROFILE
==================================================

Route:

/profile

Sections:

Goal
Experience
Skills
Study Time
Preferences

Actions:

Edit Profile
Add Skill
Update Skill
Remove Skill


--------------------------------------------------
14.1 SKILL DISPLAY
--------------------------------------------------

Example:

Python
████████░░ 80%

SQL
██████░░░░ 60%

Statistics
███░░░░░░░ 30%

Use meaningful visual indicators.

Do not fake values.

All values must come from backend data.


==================================================
15. SCREEN 05 — SKILL GAP ANALYSIS
==================================================

Route:

/skill-gaps

Purpose:

Show the learner:

Where I am
Where I need to be
What I am missing

This screen should be visually important.


--------------------------------------------------
15.1 SUMMARY
--------------------------------------------------

Display:

Target Role

Skills Required

Skills Strong

Skills Moderate

Skills Weak

Skills Missing


--------------------------------------------------
15.2 SKILL GAP LIST
--------------------------------------------------

Each skill should show:

Skill Name
Current Level
Required Level
Gap
Importance
Priority


Example:

Statistics

Current:
35%

Required:
80%

Gap:
45%

Priority:
High


--------------------------------------------------
15.3 GAP VISUALIZATION
--------------------------------------------------

Use a clear comparison visualization.

Example:

Current      Required

████░░░░░░   ████████░░

Do not use charts merely for decoration.


--------------------------------------------------
15.4 SKILL GRAPH
--------------------------------------------------

Show dependencies where useful.

Example:

Statistics
    ↓
Machine Learning
    ↓
Deep Learning

The learner should understand why sequence matters.


==================================================
16. SCREEN 06 — ROADMAP
==================================================

Route:

/roadmap

This is the core PathFinder screen.

The roadmap must communicate:

What to learn
When to learn
Why to learn
What is unlocked
What is blocked
What comes next


--------------------------------------------------
16.1 ROADMAP HEADER
--------------------------------------------------

Show:

Target Role
Roadmap Version
Estimated Duration
Overall Progress

Primary CTA:

"Continue Learning"


--------------------------------------------------
16.2 ROADMAP STRUCTURE
--------------------------------------------------

Use vertical timeline / connected roadmap.

Example:

01 Python for ML
       ↓
02 Statistics & Probability
       ↓
03 Data Processing
       ↓
04 Machine Learning
       ↓
05 Model Evaluation
       ↓
06 Deep Learning
       ↓
07 Generative AI
       ↓
08 MLOps
       ↓
09 Capstone Project


--------------------------------------------------
16.3 ROADMAP ITEM STATES
--------------------------------------------------

LOCKED

Show:

lock icon
prerequisite reason

Example:

"Complete Statistics first."


AVAILABLE

Show:

"Start Learning"


IN_PROGRESS

Show:

progress
continue action


COMPLETED

Show:

checkmark
completion information


NEEDS_REVIEW

Show:

warning
"Review this skill"


--------------------------------------------------
16.4 ROADMAP ITEM
--------------------------------------------------

Each item may contain:

Skill
Resource
Project
Assessment
Estimated Time
Status
Progress
Why this step
Prerequisites


--------------------------------------------------
16.5 EXPLANATION
--------------------------------------------------

CTA:

"Why this step?"

Show:

Skill gap
Prerequisite fit
Goal relevance
Difficulty fit
Time fit


==================================================
17. SCREEN 07 — RESOURCE DETAIL
==================================================

Route:

/resources/:id

Show:

Title
Provider
Description
Type
Difficulty
Estimated Duration
Skills Covered
URL
Why Recommended


Actions:

Start Learning
Mark Complete
Helpful
Not Helpful


Important:

The URL must come from the backend resource record.

Do not fabricate URLs.


==================================================
18. SCREEN 08 — ASSESSMENT
==================================================

Routes:

/assessments
/assessments/:id

Assessment screen should feel focused.

Show:

Assessment Title
Skill
Difficulty
Question Count
Estimated Time


--------------------------------------------------
18.1 QUESTION
--------------------------------------------------

Show:

Question
Options
Question Number
Progress


Example:

Question 4 of 10

[Option A]
[Option B]
[Option C]
[Option D]


Actions:

Previous
Next
Submit


--------------------------------------------------
18.2 IMPORTANT
--------------------------------------------------

Never expose correct answers before submission.

Do not reveal answer through:

- HTML
- frontend state
- hidden DOM
- network response
- client-side scoring


Scoring happens on backend.


==================================================
19. SCREEN 09 — ASSESSMENT RESULT
==================================================

Route:

/assessments/:id/result

Show:

Score
Mastery
Pass/Fail
Attempt
Skill Impact


Example:

78%

Machine Learning

Good progress, but Model Evaluation
needs reinforcement.


Show:

What went well
What needs improvement
Recommended next action


CTA:

"View Updated Path"


==================================================
20. SCREEN 10 — ADAPTIVE UPDATE
==================================================

Route:

/adaptive-update

This screen demonstrates PathFinder's
most important intelligence feature.

Show:

"Your learning path has been updated."


--------------------------------------------------
20.1 BEFORE
--------------------------------------------------

Machine Learning
       ↓
Deep Learning


--------------------------------------------------
20.2 DETECTED ISSUE
--------------------------------------------------

Assessment identified weakness:

Model Evaluation

Mastery:

35%


--------------------------------------------------
20.3 UPDATED PATH
--------------------------------------------------

Machine Learning
       ↓
Model Evaluation Refresher
       ↓
Practice Assessment
       ↓
Model Comparison Project
       ↓
Deep Learning


--------------------------------------------------
20.4 EXPLANATION
--------------------------------------------------

Show:

"We adjusted your path because your assessment
indicated a weakness in Model Evaluation."


Primary CTA:

"Continue Updated Path"


==================================================
21. SCREEN 11 — DASHBOARD
==================================================

Route:

/dashboard

This is the central demonstration screen.

Dashboard must answer:

Where am I?
What am I learning?
What am I weak at?
What did I complete?
What should I do next?


--------------------------------------------------
21.1 HEADER
--------------------------------------------------

Example:

Good evening, Sumit.

Your AI/ML Engineer path is progressing.

Current Roadmap:

Version 2


--------------------------------------------------
21.2 NEXT BEST ACTION
--------------------------------------------------

This should be the most prominent section.

Example:

NEXT BEST ACTION

Complete:
Model Evaluation Refresher

Why:

High-priority skill gap
Prerequisites satisfied
Fits your available study time

CTA:

"Continue"


--------------------------------------------------
21.3 PROGRESS
--------------------------------------------------

Show:

Overall Progress
Completed Milestones
Learning Time
Current Milestone


All values must come from real application state.


--------------------------------------------------
21.4 SKILL GROWTH
--------------------------------------------------

Show improvement over time.

Example:

Python
60 → 75

Statistics
30 → 55

Machine Learning
20 → 48


--------------------------------------------------
21.5 WEAK AREAS
--------------------------------------------------

Show top weak skills.

Example:

Statistics
Model Evaluation
MLOps


--------------------------------------------------
21.6 MILESTONES
--------------------------------------------------

Show:

Completed
In Progress
Upcoming


--------------------------------------------------
21.7 DASHBOARD RULE
--------------------------------------------------

Do not add meaningless metrics such as:

"AI Power: 97%"
"Learning IQ: 89%"
"Productivity Score: 94%"

unless backed by actual product logic.


==================================================
22. SCREEN 12 — AI ASSISTANT
==================================================

Route:

/assistant

The assistant should feel integrated with
PathFinder, not like a generic chatbot.


--------------------------------------------------
22.1 CHAT HEADER
--------------------------------------------------

PathFinder AI

Context-aware learning assistant


--------------------------------------------------
22.2 SUGGESTED QUESTIONS
--------------------------------------------------

Examples:

"What should I study today?"

"Why was this resource recommended?"

"Why do I need statistics first?"

"What should I do after this assessment?"

"Explain my biggest skill gap."


--------------------------------------------------
22.3 CHAT
--------------------------------------------------

Messages:

User
Assistant

Show loading state:

"Thinking about your learning path..."


--------------------------------------------------
22.4 CONTEXT INDICATOR
--------------------------------------------------

Optionally show:

Using your roadmap
Using your skill gaps
Using your recent assessment

Do not expose internal prompts or technical
implementation details.


==================================================
23. SCREEN 13 — PROFILE / SETTINGS
==================================================

Routes:

/profile
/settings

Profile:

Name
Email
Goal
Experience
Skills
Study Time
Preferences


Settings:

Account
Preferences
Theme
Notifications
Logout


Keep settings simple.

Do not build unnecessary enterprise settings.


==================================================
24. GLOBAL COMPONENTS
==================================================

Create reusable:

Button
Input
Select
Textarea
Modal
Dialog
Card
Badge
ProgressBar
ProgressRing
Tabs
Tooltip
Dropdown
Toast
Skeleton
EmptyState
ErrorState
LoadingState
ConfirmDialog
Avatar
Breadcrumb
Timeline
SkillBadge
RoadmapNode
ResourceCard
AssessmentCard
RecommendationCard


==================================================
25. COMPONENT RULE
==================================================

Do not duplicate UI patterns.

If the same component appears twice,
make it reusable.

Example:

RecommendationCard

must be shared by:

Dashboard
Recommendations
Roadmap


==================================================
26. LOADING STATES
==================================================

Every API-driven screen must have a loading state.

Use:

Skeletons
Spinners where appropriate
Progressive rendering


Do not show blank white screens.


==================================================
27. ERROR STATES
==================================================

Every API-driven screen must have an error state.

Example:

"Unable to load your roadmap."

Actions:

Retry

Do not silently show empty content when an API fails.


==================================================
28. EMPTY STATES
==================================================

Examples:

No roadmap:

"Your learning path hasn't been created yet."

CTA:

"Build My Learning Path"


No recommendations:

"No recommendations are available right now."

CTA:

"Recalculate Recommendations"


No assessments:

"No assessments are available for your current path."


==================================================
29. SUCCESS FEEDBACK
==================================================

After meaningful actions:

Profile saved
Skill updated
Roadmap generated
Assessment submitted
Resource feedback saved

Use subtle toast / inline confirmation.

Do not overuse animations.


==================================================
30. MODALS
==================================================

Use modals only for:

- confirmations
- important explanations
- focused interactions

Do not put entire application pages inside
large modal windows.


==================================================
31. CHARTS
==================================================

Use Recharts only where charts communicate
meaningful learning information.

Good:

Skill growth
Progress over time
Current vs required proficiency

Avoid:

Decorative pie charts
Fake analytics
Unnecessary graphs


==================================================
32. ROADMAP VISUALIZATION
==================================================

Roadmap connections must clearly communicate
dependency and sequence.

Desktop:

Vertical timeline.

Mobile:

Simplified vertical timeline.

Do not rely only on connecting lines.

Each node should have:

number
status
title
skill
action


==================================================
33. RESPONSIVE SIDEBAR
==================================================

Desktop:

Fixed/collapsible sidebar.

Tablet:

Collapsible sidebar.

Mobile:

Drawer.

The navigation must remain usable without
horizontal scrolling.


==================================================
34. MOBILE DASHBOARD
==================================================

Order content:

1. Greeting
2. Next Best Action
3. Progress
4. Current Milestone
5. Skill Gaps
6. Roadmap Preview
7. Assistant CTA


==================================================
35. MOBILE ROADMAP
==================================================

Use:

vertical stack

Each item should show:

status
title
progress
action

Do not attempt to maintain a wide desktop
roadmap layout on mobile.


==================================================
36. FORMS
==================================================

Use:

React Hook Form

and:

Zod

for client-side validation.

Backend remains authoritative.

Never rely only on frontend validation.


==================================================
37. API CLIENT
==================================================

Create:

src/api/client.ts

All requests should go through the centralized
API client.

Do not scatter:

fetch()

calls across components.

Example conceptual API:

api.auth.login()
api.profile.get()
api.profile.update()
api.skillGaps.analyze()
api.roadmaps.generate()
api.recommendations.list()
api.assessments.submit()
api.progress.get()
api.assistant.chat()


==================================================
38. SERVER STATE
==================================================

Use TanStack Query or equivalent
server-state management.

Handle:

loading
error
success
cache
refetch
mutation

Do not duplicate server state unnecessarily
inside React local state.


==================================================
39. TYPES
==================================================

Frontend types must reflect backend schemas.

Create:

src/types/

auth.ts
profile.ts
skill.ts
role.ts
resource.ts
roadmap.ts
recommendation.ts
assessment.ts
progress.ts
assistant.ts
api.ts


==================================================
40. AUTH STATE
==================================================

Create centralized authentication state.

It should know:

authenticated
unauthenticated
loading

Protected routes must redirect unauthenticated
users to:

/login


==================================================
41. PROTECTED ROUTES
==================================================

Protect:

/dashboard
/roadmap
/skill-gaps
/resources
/assessments
/assistant
/profile
/settings


==================================================
42. ONBOARDING GUARD
==================================================

If authenticated user has no completed learner
profile/goal:

redirect to:

/onboarding

After onboarding:

redirect to:

/dashboard


==================================================
43. FRONTEND SECURITY
==================================================

Never put secrets in frontend environment variables.

Do NOT expose:

LLM API keys
database credentials
JWT signing secrets
private provider keys

Frontend only receives public/client-safe values.


==================================================
44. ACCESSIBILITY
==================================================

Consider accessibility during development.

Required:

Keyboard navigation
Semantic HTML
Readable typography
Accessible labels
Sufficient contrast
Meaningful error messages
Accessible buttons
Focus states

Forms must have labels.

Do not rely solely on placeholder text.

Dialogs must be keyboard accessible.


==================================================
45. ANIMATION
==================================================

Use subtle animation for:

page transitions
loading
roadmap completion
toast appearance
interactive feedback

Avoid:

constant floating elements
excessive motion
large animated backgrounds
animation on every component

Animation must not reduce usability.


==================================================
46. DATA INTEGRITY IN UI
==================================================

Never fake:

skill gaps
progress
assessment scores
roadmap sequence
recommendation ranking
adaptive updates

These must come from backend logic.

Curated demo data may be used for:

skill catalog
resource catalog
project catalog
assessment questions


==================================================
47. API ERROR MAPPING
==================================================

Map backend error codes to user-friendly UI.

Example:

AUTH_INVALID_CREDENTIALS

→

"Email or password is incorrect."


PROFILE_INCOMPLETE

→

"Complete your profile before generating
a learning path."


GOAL_ANALYSIS_FAILED

→

"We couldn't understand that goal.
Please try again."


PREREQUISITE_NOT_MET

→

"Complete the required prerequisite first."


AI_SERVICE_UNAVAILABLE

→

"PathFinder AI is temporarily unavailable.
You can continue using your existing roadmap."


RATE_LIMIT_EXCEEDED

→

"Too many requests. Please try again shortly."


==================================================
48. FRONTEND PERFORMANCE
==================================================

First prioritize correctness.

Then optimize:

- unnecessary re-renders
- API requests
- image sizes
- bundle size
- chart rendering
- roadmap rendering

Do not prematurely optimize.


==================================================
49. IMAGE POLICY
==================================================

Do not use random stock images.

Use visuals only when they improve the
product experience.

Prefer:

- product UI previews
- subtle illustrations
- meaningful icons
- skill/roadmap visualizations

Avoid decorative image overload.


==================================================
50. DASHBOARD DATA FLOW
==================================================

Dashboard:

GET /progress
GET /progress/next-action
GET /roadmaps/current
GET /recommendations
GET /progress/skills

Combine backend data.

Do not independently calculate business
logic in frontend.


==================================================
51. ROADMAP DATA FLOW
==================================================

Roadmap:

GET /roadmaps/current

User:

Start Item
    ↓
POST /roadmaps/items/{id}/start

Complete:

POST /roadmaps/items/{id}/complete

Assessment:

POST /assessments/{id}/submit

Adaptive:

Backend updates roadmap

Frontend:

refetch current roadmap
refetch dashboard
refetch progress


==================================================
52. ASSESSMENT DATA FLOW
==================================================

GET assessment
 ↓
Render questions
 ↓
User answers
 ↓
Submit
 ↓
Backend scoring
 ↓
Result
 ↓
Adaptive engine
 ↓
Updated roadmap
 ↓
Updated dashboard


==================================================
53. ASSISTANT DATA FLOW
==================================================

User message
 ↓
POST /assistant/chat
 ↓
Backend builds learner context
 ↓
RAG / AI
 ↓
Assistant response
 ↓
Display response
 ↓
Persist conversation


==================================================
54. CORE DEMO FLOW
==================================================

The UI must support this exact evaluator journey:

Landing
 ↓
Register
 ↓
Onboarding
 ↓
Goal
 ↓
Profile
 ↓
Skill Gap
 ↓
Roadmap
 ↓
Resource
 ↓
Ask "Why?"
 ↓
Assessment
 ↓
Poor Assessment
 ↓
Adaptive Update
 ↓
Dashboard
 ↓
AI Assistant


==================================================
55. DEMO UX REQUIREMENT
==================================================

The evaluator must not encounter dead ends.

Every major screen must provide a clear
next action.

Examples:

Landing:
Build My Learning Path

Onboarding:
Analyze My Goal

Profile:
Continue

Skill Gap:
Build My Roadmap

Roadmap:
Start Learning

Resource:
Start / Complete

Assessment:
Submit Assessment

Result:
View Updated Path

Adaptive:
Continue Updated Path

Dashboard:
Continue

Assistant:
Ask PathFinder


==================================================
56. PERSONALIZATION UI
==================================================

Two learners with different profiles should
visibly receive different:

- skill gaps
- roadmap sequences
- recommendations
- next actions

Do not use one static roadmap for every user.


==================================================
57. ADAPTIVE UI
==================================================

After a weak assessment:

Show clearly:

What changed
Why it changed
What to do next

Example:

BEFORE

Machine Learning
 ↓
Deep Learning

AFTER

Machine Learning
 ↓
Model Evaluation Refresher
 ↓
Practice Assessment
 ↓
Deep Learning


==================================================
58. EXPLAINABILITY UI
==================================================

For every important recommendation provide:

"Why this?"

Possible explanation:

"Your Model Evaluation skill has a 55% gap.
The prerequisites are satisfied.
This resource matches your current level
and fits your study time."


The displayed explanation must be based on
real backend signals.


==================================================
59. FRONTEND FILE STRUCTURE
==================================================

Recommended:

src/

  app/
    App.tsx
    routes.tsx

  layouts/
    PublicLayout.tsx
    AppLayout.tsx

  pages/
    Landing/
    Login/
    Register/
    Onboarding/
    Dashboard/
    Roadmap/
    SkillGaps/
    Resources/
    ResourceDetail/
    Assessments/
    Assessment/
    AssessmentResult/
    AdaptiveUpdate/
    Assistant/
    Profile/
    Settings/

  components/
    ui/
    navigation/
    dashboard/
    roadmap/
    skills/
    resources/
    assessments/
    assistant/
    onboarding/

  features/
    auth/
    onboarding/
    learner/
    roadmap/
    recommendations/
    assessments/
    progress/
    assistant/

  api/
    client.ts
    auth.ts
    profile.ts
    roadmap.ts
    recommendations.ts
    assessments.ts
    progress.ts
    assistant.ts
    resources.ts
    skills.ts

  hooks/

  types/

  lib/

  utils/

  styles/


==================================================
60. UI STATE MODEL
==================================================

Every API-driven feature should support:

idle
loading
success
empty
error

Example:

Roadmap:

idle
 ↓
loading
 ↓
success

or:

loading
 ↓
error
 ↓
retry
 ↓
success


==================================================
61. NO FAKE UI
==================================================

Do NOT implement UI-only buttons such as:

"Generate AI Roadmap"

if the button does not call the actual
backend functionality.

Do NOT implement:

fake loading for AI
fake progress
fake assessment result
fake adaptive update
fake recommendation explanation

If functionality is unavailable:

show a clear limitation/fallback.


==================================================
62. NO UNNECESSARY FEATURES
==================================================

Do not add:

social feed
learner messaging
marketplace
payments
full LMS
video hosting
live classes
native mobile app
enterprise admin portal
microservice-specific UI

unless explicitly required later.


==================================================
63. P0 UI PRIORITY
==================================================

P0:

Authentication
AI onboarding
Learner profile
Goal extraction
Skill gap
Skill graph
Recommendations
Personalized roadmap
Explanation
Assessment
Progress
Adaptive roadmap
Dashboard
AI assistant


==================================================
64. P1 UI PRIORITY
==================================================

P1:

Resource feedback
Project recommendations
Roadmap history
Responsive mobile polish
Advanced charts


==================================================
65. P2 UI PRIORITY
==================================================

P2:

Resume analysis
GitHub analysis
Voice assistant
Gamification
Certification recommendations
Career market analysis


P2 must never delay P0.


==================================================
66. UI TESTING
==================================================

Test using:

Desktop
Tablet
Mobile

Test:

- navigation
- forms
- buttons
- loading
- errors
- charts
- roadmap
- modals
- scrolling
- typography
- accessibility


==================================================
67. E2E TEST
==================================================

Critical E2E:

Landing
 ↓
Register
 ↓
Onboarding
 ↓
Goal
 ↓
Roadmap
 ↓
Assessment
 ↓
Adaptive Update
 ↓
Dashboard
 ↓
Assistant

The entire flow must work without manually
editing the database.


==================================================
68. FRONTEND DEFINITION OF DONE
==================================================

[ ] Landing page complete
[ ] Login complete
[ ] Register complete
[ ] Authentication state works
[ ] Protected routes work
[ ] Onboarding complete
[ ] Natural-language goal input works
[ ] Goal analysis result displayed
[ ] Profile editing works
[ ] Skill management works
[ ] Skill gap screen works
[ ] Skill graph works
[ ] Roadmap screen works
[ ] Roadmap states work
[ ] Resource detail works
[ ] Recommendation explanation works
[ ] Assessment UI works
[ ] Correct answers never exposed
[ ] Assessment result works
[ ] Adaptive update screen works
[ ] Dashboard works
[ ] Next-best-action works
[ ] Skill growth visualization works
[ ] AI Assistant works
[ ] Conversation history works
[ ] Profile works
[ ] Settings works
[ ] Loading states implemented
[ ] Error states implemented
[ ] Empty states implemented
[ ] Responsive desktop layout works
[ ] Responsive tablet layout works
[ ] Responsive mobile layout works
[ ] Accessibility basics implemented
[ ] No fake metrics
[ ] No fake AI functionality
[ ] No broken navigation
[ ] API integration centralized
[ ] Frontend tests pass
[ ] Critical E2E flow passes


==================================================
69. FINAL FRONTEND EXPERIENCE
==================================================

The final UI should feel like:

A modern intelligent learning navigation
platform.

Not:

A course listing website.

Not:

A generic dashboard.

Not:

A chatbot wrapper.

The most important visual story is:

GOAL
 ↓
CURRENT STATE
 ↓
SKILL GAP
 ↓
LEARNING PATH
 ↓
PROGRESS
 ↓
ASSESSMENT
 ↓
ADAPTATION
 ↓
NEXT BEST ACTION


==================================================
END OF FRONTEND_SPEC.md
==================================================