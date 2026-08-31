# PathFinder AI — Seed Data Specification

Document: SEED_DATA_SPEC.md
Version: 1.0
Status: Implementation Specification
Project: PathFinder AI

==================================================
1. PURPOSE
==================================================

This document defines the curated seed data required
to make the PathFinder MVP functional and demonstrable.

Seed data must provide enough structured information
for the following real flows:

Goal
 ↓
Role
 ↓
Required Skills
 ↓
Skill Gaps
 ↓
Prerequisites
 ↓
Resources
 ↓
Recommendations
 ↓
Roadmap
 ↓
Assessment
 ↓
Mastery
 ↓
Adaptive Learning

Seed data is product data.

It must NOT be used to fake:

- learner progress
- assessment results
- recommendations
- adaptive changes
- personalized dashboard metrics


==================================================
2. SEED DATA PRINCIPLES
==================================================

Use deterministic curated data.

The same database seed should produce the same
catalog and dependency graph.

Seed data must be:

- internally consistent
- realistic
- logically connected
- sufficient for the MVP
- easy to extend
- easy to reset

Do not create hundreds of unnecessary records.

Quality > quantity.


==================================================
3. SEED DATA CATEGORIES
==================================================

Required:

1. Roles
2. Skills
3. Skill Dependencies
4. Role-Skill Requirements
5. Resources
6. Projects
7. Assessments
8. Assessment Questions
9. Resource-Skill Mappings
10. Project-Skill Mappings
11. Resource Prerequisites
12. Demo configuration


==================================================
4. PRIMARY DEMO ROLE
==================================================

Primary role:

AI/ML Engineer

Slug:

ai-ml-engineer

Description:

An AI/ML Engineer develops machine learning
systems, prepares data, evaluates models,
works with deep learning and modern AI systems,
and understands deployment and production
considerations.


==================================================
5. ROLE REQUIREMENTS
==================================================

The primary role should require the following
skills.

Skill                    Required Level
--------------------------------------------------
Python                   80
Programming Fundamentals 70
SQL                      65
Statistics               75
Probability              70
Data Processing          75
Machine Learning         80
Model Evaluation         75
Feature Engineering      70
Deep Learning            70
NLP                      60
Computer Vision          60
Generative AI            70
MLOps                    60
Git                      65
APIs                     60
Docker                   55
System Design            50


==================================================
6. SKILL CATALOG
==================================================

Create the following skills.

--------------------------------------------------
6.1 Programming Fundamentals
--------------------------------------------------

Slug:

programming-fundamentals

Category:

Programming

Description:

Core programming concepts including variables,
conditions, loops, functions, data structures
and problem solving.


--------------------------------------------------
6.2 Python
--------------------------------------------------

Slug:

python

Category:

Programming

Description:

Python programming for data processing,
automation and machine learning workflows.


--------------------------------------------------
6.3 SQL
--------------------------------------------------

Slug:

sql

Category:

Data

Description:

Relational querying, joins, aggregations,
subqueries and analytical SQL.


--------------------------------------------------
6.4 Statistics
--------------------------------------------------

Slug:

statistics

Category:

Mathematics

Description:

Descriptive statistics, distributions,
variance, correlation, hypothesis testing
and statistical reasoning.


--------------------------------------------------
6.5 Probability
--------------------------------------------------

Slug:

probability

Category:

Mathematics

Description:

Probability fundamentals, conditional
probability, Bayes theorem and distributions.


--------------------------------------------------
6.6 Data Processing
--------------------------------------------------

Slug:

data-processing

Category:

Data

Description:

Data cleaning, transformation, missing values,
encoding, scaling and dataset preparation.


--------------------------------------------------
6.7 Machine Learning
--------------------------------------------------

Slug:

machine-learning

Category:

Machine Learning

Description:

Supervised and unsupervised learning,
training workflows and model selection.


--------------------------------------------------
6.8 Model Evaluation
--------------------------------------------------

Slug:

model-evaluation

Category:

Machine Learning

Description:

Evaluation metrics, validation, cross-validation,
confusion matrix, precision, recall, F1 and
model comparison.


--------------------------------------------------
6.9 Feature Engineering
--------------------------------------------------

Slug:

feature-engineering

Category:

Machine Learning

Description:

Feature creation, transformation, selection
and representation.


--------------------------------------------------
6.10 Deep Learning
--------------------------------------------------

Slug:

deep-learning

Category:

Deep Learning

Description:

Neural networks, optimization, CNNs, RNNs,
transformers and deep learning workflows.


--------------------------------------------------
6.11 NLP
--------------------------------------------------

Slug:

nlp

Category:

AI

Description:

Natural language processing, tokenization,
embeddings, sequence modeling and transformer
applications.


--------------------------------------------------
6.12 Computer Vision
--------------------------------------------------

Slug:

computer-vision

Category:

AI

Description:

Image representation, classification,
object detection and visual feature learning.


--------------------------------------------------
6.13 Generative AI
--------------------------------------------------

Slug:

generative-ai

Category:

AI

Description:

Large language models, prompting, embeddings,
RAG and generative AI application development.


--------------------------------------------------
6.14 MLOps
--------------------------------------------------

Slug:

mlops

Category:

Production AI

Description:

Model deployment, monitoring, reproducibility,
pipelines and production ML operations.


--------------------------------------------------
6.15 Git
--------------------------------------------------

Slug:

git

Category:

Developer Tools

Description:

Version control, branching, commits and
collaboration workflows.


--------------------------------------------------
6.16 APIs
--------------------------------------------------

Slug:

apis

Category:

Backend

Description:

HTTP APIs, REST principles, requests,
responses, authentication and integration.


--------------------------------------------------
6.17 Docker
--------------------------------------------------

Slug:

docker

Category:

DevOps

Description:

Containerization, images, containers and
basic deployment workflows.


--------------------------------------------------
6.18 System Design
--------------------------------------------------

Slug:

system-design

Category:

Software Engineering

Description:

Basic system architecture, scalability,
components, APIs, databases and tradeoffs.


==================================================
7. SKILL DEPENDENCY GRAPH
==================================================

The dependency graph must be represented
explicitly.

Core graph:

Programming Fundamentals
        ↓
      Python
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


Mathematical graph:

Probability
     ↓
Statistics
     ↓
Machine Learning


Additional graph:

Python
  ↓
NLP

Python
  ↓
Computer Vision

Machine Learning
  ↓
Feature Engineering

Git
  ↓
APIs
  ↓
MLOps

Docker
  ↓
MLOps

APIs
  ↓
System Design


==================================================
8. DEPENDENCY THRESHOLDS
==================================================

Recommended prerequisite thresholds:

Programming Fundamentals → Python

required mastery:

60


Python → Data Processing

required mastery:

60


Statistics → Machine Learning

required mastery:

60


Probability → Statistics

required mastery:

50


Data Processing → Machine Learning

required mastery:

60


Machine Learning → Model Evaluation

required mastery:

60


Machine Learning → Feature Engineering

required mastery:

60


Machine Learning → Deep Learning

required mastery:

70


Deep Learning → Generative AI

required mastery:

60


Git → MLOps

required mastery:

60


Docker → MLOps

required mastery:

50


APIs → MLOps

required mastery:

50


==================================================
9. ROLE-SKILL MAPPING
==================================================

AI/ML Engineer must contain all primary
skills listed below.

Required:

Python = 80
SQL = 65
Statistics = 75
Probability = 70
Data Processing = 75
Machine Learning = 80
Model Evaluation = 75
Feature Engineering = 70
Deep Learning = 70
NLP = 60
Computer Vision = 60
Generative AI = 70
MLOps = 60
Git = 65
APIs = 60
Docker = 55
System Design = 50

Optional supporting skill:

Programming Fundamentals = 70


==================================================
10. RESOURCE TYPES
==================================================

Supported:

COURSE
TUTORIAL
DOCUMENTATION
ARTICLE
VIDEO
PROJECT
PRACTICE
ASSESSMENT


==================================================
11. RESOURCE DATA RULE
==================================================

Every resource must contain:

title
description
resource_type
difficulty
estimated_minutes
skills
prerequisites
url
provider
active


Do not fabricate URLs.

URLs must be verified before being inserted.

If a resource URL cannot be verified:

do not seed it as an external resource.

Use a clearly marked internal/demo resource
instead.


==================================================
12. RESOURCE DIFFICULTY
==================================================

Allowed:

BEGINNER
INTERMEDIATE
ADVANCED


==================================================
13. RESOURCE SET — PROGRAMMING
==================================================

Resource:

Python Fundamentals

Type:

COURSE

Difficulty:

BEGINNER

Skills:

Programming Fundamentals
Python

Prerequisites:

none


Resource:

Python for Data Work

Type:

TUTORIAL

Difficulty:

INTERMEDIATE

Skills:

Python
Data Processing

Prerequisites:

Python


==================================================
14. RESOURCE SET — MATHEMATICS
==================================================

Resource:

Statistics Foundations

Type:

COURSE

Difficulty:

BEGINNER

Skills:

Statistics

Prerequisites:

Probability


Resource:

Probability Essentials

Type:

COURSE

Difficulty:

BEGINNER

Skills:

Probability

Prerequisites:

none


Resource:

Statistics for Machine Learning

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Statistics
Probability

Prerequisites:

Probability


==================================================
15. RESOURCE SET — DATA
==================================================

Resource:

Data Cleaning and Preparation

Type:

TUTORIAL

Difficulty:

BEGINNER

Skills:

Data Processing
Python

Prerequisites:

Python


Resource:

SQL for Data Analysis

Type:

COURSE

Difficulty:

BEGINNER

Skills:

SQL

Prerequisites:

Programming Fundamentals


==================================================
16. RESOURCE SET — MACHINE LEARNING
==================================================

Resource:

Machine Learning Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Machine Learning
Statistics
Data Processing

Prerequisites:

Statistics
Data Processing


Resource:

Supervised Learning Practice

Type:

PRACTICE

Difficulty:

INTERMEDIATE

Skills:

Machine Learning

Prerequisites:

Machine Learning


Resource:

Model Evaluation Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Model Evaluation
Machine Learning

Prerequisites:

Machine Learning


Resource:

Feature Engineering Workshop

Type:

TUTORIAL

Difficulty:

INTERMEDIATE

Skills:

Feature Engineering
Machine Learning

Prerequisites:

Machine Learning


==================================================
17. RESOURCE SET — DEEP LEARNING
==================================================

Resource:

Neural Networks Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Deep Learning

Prerequisites:

Machine Learning
Model Evaluation


Resource:

Deep Learning Practice

Type:

PRACTICE

Difficulty:

INTERMEDIATE

Skills:

Deep Learning

Prerequisites:

Deep Learning


==================================================
18. RESOURCE SET — NLP
==================================================

Resource:

NLP Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

NLP
Python

Prerequisites:

Python
Machine Learning


Resource:

Text Classification Project

Type:

PROJECT

Difficulty:

INTERMEDIATE

Skills:

NLP
Machine Learning

Prerequisites:

NLP


==================================================
19. RESOURCE SET — COMPUTER VISION
==================================================

Resource:

Computer Vision Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Computer Vision
Deep Learning

Prerequisites:

Deep Learning


Resource:

Image Classification Project

Type:

PROJECT

Difficulty:

INTERMEDIATE

Skills:

Computer Vision
Deep Learning

Prerequisites:

Computer Vision


==================================================
20. RESOURCE SET — GENERATIVE AI
==================================================

Resource:

Generative AI Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

Generative AI

Prerequisites:

Deep Learning


Resource:

Embeddings and Semantic Search

Type:

TUTORIAL

Difficulty:

INTERMEDIATE

Skills:

Generative AI
APIs

Prerequisites:

Machine Learning


Resource:

RAG Application Project

Type:

PROJECT

Difficulty:

ADVANCED

Skills:

Generative AI
APIs

Prerequisites:

Generative AI
APIs


==================================================
21. RESOURCE SET — MLOPS
==================================================

Resource:

Git for ML Projects

Type:

TUTORIAL

Difficulty:

BEGINNER

Skills:

Git

Prerequisites:

none


Resource:

Docker Fundamentals

Type:

TUTORIAL

Difficulty:

BEGINNER

Skills:

Docker

Prerequisites:

none


Resource:

ML Deployment Fundamentals

Type:

COURSE

Difficulty:

ADVANCED

Skills:

MLOps
APIs
Docker

Prerequisites:

Machine Learning
APIs
Docker


==================================================
22. RESOURCE SET — SYSTEM DESIGN
==================================================

Resource:

System Design Fundamentals

Type:

COURSE

Difficulty:

INTERMEDIATE

Skills:

System Design
APIs

Prerequisites:

APIs


==================================================
23. PROJECT CATALOG
==================================================

Create practical projects because PathFinder
should recommend learning-by-doing resources.


--------------------------------------------------
23.1 PROJECT — DATA CLEANING PIPELINE
--------------------------------------------------

Title:

Data Cleaning Pipeline

Difficulty:

BEGINNER

Skills:

Python
Data Processing
SQL

Prerequisites:

Python


Goal:

Build a reproducible data cleaning pipeline.


--------------------------------------------------
23.2 PROJECT — ML CLASSIFICATION
--------------------------------------------------

Title:

End-to-End ML Classification

Difficulty:

INTERMEDIATE

Skills:

Machine Learning
Statistics
Model Evaluation
Feature Engineering

Prerequisites:

Machine Learning
Model Evaluation


Goal:

Build, evaluate and compare classification
models.


--------------------------------------------------
23.3 PROJECT — MODEL EVALUATION LAB
--------------------------------------------------

Title:

Model Evaluation Lab

Difficulty:

INTERMEDIATE

Skills:

Model Evaluation

Prerequisites:

Machine Learning


Goal:

Compare multiple models using appropriate
evaluation metrics.


--------------------------------------------------
23.4 PROJECT — NLP APPLICATION
--------------------------------------------------

Title:

NLP Text Classification

Difficulty:

INTERMEDIATE

Skills:

NLP
Machine Learning
Python

Prerequisites:

Machine Learning
NLP


--------------------------------------------------
23.5 PROJECT — RAG ASSISTANT
--------------------------------------------------

Title:

Document Q&A RAG Assistant

Difficulty:

ADVANCED

Skills:

Generative AI
APIs
NLP

Prerequisites:

Generative AI
APIs


--------------------------------------------------
23.6 PROJECT — ML DEPLOYMENT
--------------------------------------------------

Title:

Deploy an ML Model with API and Docker

Difficulty:

ADVANCED

Skills:

MLOps
APIs
Docker

Prerequisites:

Machine Learning
APIs
Docker


==================================================
24. ASSESSMENT CATALOG
==================================================

Required assessments:

1. Python Fundamentals Check
2. Statistics Foundations Check
3. Machine Learning Fundamentals
4. Model Evaluation Assessment
5. Deep Learning Fundamentals
6. Generative AI Fundamentals
7. MLOps Foundations


==================================================
25. ASSESSMENT CONFIGURATION
==================================================

Default:

10 questions

Passing score:

60%

Mastery score:

80%

Assessment difficulty:

match learner level where possible.


==================================================
26. ASSESSMENT — PYTHON
==================================================

Title:

Python Fundamentals Check

Skill:

Python

Questions:

10


Example topics:

variables
conditions
loops
functions
lists
dictionaries
exceptions
basic data processing


==================================================
27. ASSESSMENT — STATISTICS
==================================================

Title:

Statistics Foundations Check

Skill:

Statistics

Questions:

10


Topics:

mean
median
variance
standard deviation
distributions
correlation
sampling
hypothesis testing


==================================================
28. ASSESSMENT — MACHINE LEARNING
==================================================

Title:

Machine Learning Fundamentals

Skill:

Machine Learning

Questions:

10


Topics:

supervised learning
unsupervised learning
classification
regression
training
validation
overfitting
underfitting


==================================================
29. ASSESSMENT — MODEL EVALUATION
==================================================

Title:

Model Evaluation Assessment

Skill:

Model Evaluation

Questions:

10


Topics:

accuracy
precision
recall
F1
confusion matrix
cross-validation
ROC/AUC
model comparison


==================================================
30. ASSESSMENT — DEEP LEARNING
==================================================

Title:

Deep Learning Fundamentals

Skill:

Deep Learning

Questions:

10


Topics:

neurons
activation functions
backpropagation
loss
optimization
CNN
RNN
transformers


==================================================
31. ASSESSMENT — GENERATIVE AI
==================================================

Title:

Generative AI Fundamentals

Skill:

Generative AI

Questions:

10


Topics:

LLMs
prompting
embeddings
vector search
RAG
context
hallucination
grounding


==================================================
32. ASSESSMENT — MLOPS
==================================================

Title:

MLOps Foundations

Skill:

MLOps

Questions:

10


Topics:

deployment
containers
monitoring
versioning
reproducibility
pipelines


==================================================
33. QUESTION DATA STRUCTURE
==================================================

Each question must contain:

question
question_type
options
correct_option
explanation
difficulty
skill_id


Supported question types:

MCQ

Future types may include:

MULTI_SELECT
TRUE_FALSE
SHORT_ANSWER


For MVP:

Use MCQ.

==================================================
34. QUESTION QUALITY RULES
==================================================

Questions must:

- test actual understanding
- have one clearly correct answer
- contain plausible distractors
- avoid ambiguous wording
- avoid trick questions
- include explanation

Do not create questions where:

two options are technically correct.

==================================================
35. SAMPLE QUESTIONS
==================================================

Question:

Which metric is especially useful when false
positives and false negatives both matter?

Options:

A. Accuracy
B. Precision
C. F1 Score
D. Mean Absolute Error

Correct:

C

Explanation:

F1 combines precision and recall into a single
measure and is useful when both matter.


--------------------------------------------------

Question:

What is overfitting?

Options:

A. Model performs poorly on training data
B. Model memorizes training patterns and
   generalizes poorly
C. Model has too few parameters
D. Dataset contains no labels

Correct:

B


--------------------------------------------------

Question:

Which technique is commonly used to reduce
the effect of different feature scales?

Options:

A. Scaling
B. Tokenization
C. Bagging
D. Sampling

Correct:

A


==================================================
36. ADAPTIVE TEST DATA
==================================================

The dataset must support a deterministic weak
assessment scenario.

For example:

Model Evaluation Assessment

Correct answers:

3 / 10

Expected score:

30%

Expected mastery:

FOUNDATIONAL_INTERVENTION


==================================================
37. STRONG ASSESSMENT SCENARIO
==================================================

Same assessment:

9 / 10

Expected:

90%

Expected mastery:

MASTERED


This scenario should not introduce unnecessary
reinforcement.


==================================================
38. MEDIUM ASSESSMENT SCENARIO
==================================================

Same assessment:

6 / 10

Expected:

60%

Expected:

CONTINUE

depending on configured boundary behavior.


==================================================
39. DEMO LEARNER
==================================================

Create optional demo learner:

Name:

Demo Learner

Email:

demo@pathfinder.local


IMPORTANT:

This account must be clearly marked as demo data.

Never present it as a real user.


==================================================
40. DEMO LEARNER PROFILE
==================================================

Target Role:

AI/ML Engineer

Experience:

Beginner / Early Intermediate

Study Time:

2 hours/day


Current skills:

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


This profile intentionally contains gaps so
the recommendation and roadmap engines
have meaningful work to perform.


==================================================
41. EXPECTED DEMO SKILL GAPS
==================================================

High-priority gaps should include:

Model Evaluation
Machine Learning
Statistics
Data Processing
Probability
Generative AI
MLOps


The exact ranking must be calculated by the
recommendation engine.

Do not hardcode ranking.


==================================================
42. EXPECTED DEMO ROADMAP
==================================================

The generated roadmap should approximately
follow dependency logic:

Probability
 ↓
Statistics
 ↓
Data Processing
 ↓
Machine Learning
 ↓
Model Evaluation
 ↓
Feature Engineering
 ↓
Deep Learning
 ↓
Generative AI
 ↓
APIs
 ↓
Docker
 ↓
MLOps
 ↓
Capstone


The exact roadmap is generated by the
roadmap engine.

This list is only the intended dependency
structure.


==================================================
43. DEMO ADAPTIVE SCENARIO
==================================================

Initial:

Model Evaluation

Current mastery:

25%


Learner completes:

Model Evaluation Assessment


Scenario:

3 / 10 correct


Expected:

30%

System detects:

FOUNDATIONAL_INTERVENTION


System recommends:

1. Model Evaluation refresher
2. Practice questions
3. Model comparison project
4. Reassessment


Deep Learning remains dependent on required
prerequisites.


==================================================
44. DEMO SUCCESS SCENARIO
==================================================

After reinforcement:

Model Evaluation assessment:

9 / 10


Expected:

90%

System:

Marks skill MASTERED.

Roadmap should allow progression to the
next eligible milestone.


==================================================
45. RESOURCE FEEDBACK DATA
==================================================

Do not seed fake learner feedback.

Only seed:

resource catalog data.

User feedback must be generated by actual
user interaction.


==================================================
46. RESOURCE RATING
==================================================

If rating system is implemented:

Do not pre-populate fake user ratings.

If external verified metadata exists,
store it separately from user-generated rating.

Otherwise:

leave rating empty.


==================================================
47. DEMO DATA IDENTIFIERS
==================================================

Use stable slugs.

Examples:

role:

ai-ml-engineer


skills:

python
statistics
machine-learning
model-evaluation
deep-learning
generative-ai
mlops


resources:

python-fundamentals
statistics-foundations
ml-fundamentals
model-evaluation-fundamentals
neural-networks-fundamentals
generative-ai-fundamentals
ml-deployment-fundamentals


This makes seed scripts idempotent.


==================================================
48. SEED SCRIPT BEHAVIOR
==================================================

Seed script must be idempotent.

Running:

python scripts/seed.py

once:

creates data.


Running again:

must not create duplicates.


Use:

stable slugs
unique constraints
upsert logic


==================================================
49. SEED ORDER
==================================================

Insert in this order:

1. Skills
2. Roles
3. Role-Skill Requirements
4. Skill Dependencies
5. Resources
6. Resource-Skill Mappings
7. Resource Prerequisites
8. Projects
9. Project-Skill Mappings
10. Assessments
11. Questions
12. Optional demo learner
13. Optional demo learner skills


==================================================
50. SEED VALIDATION
==================================================

After seeding verify:

Every role has required skills.

Every required skill exists.

Every dependency references valid skills.

Every resource references valid skills.

Every prerequisite references valid skills.

Every project references valid skills.

Every assessment references valid skills.

Every question references valid assessment.


==================================================
51. ORPHAN DATA TEST
==================================================

The seed validator must detect:

resource without skill
project without skill
role without required skill
dependency without parent
dependency without child
assessment without skill
question without assessment


Expected:

Seed validation failure.


==================================================
52. DEPENDENCY CYCLE VALIDATION
==================================================

After seed:

Run dependency graph validation.

Expected:

No cycles.


If a cycle exists:

seed process must fail.

Do not silently accept invalid graph.


==================================================
53. RESOURCE URL VALIDATION
==================================================

Before production/demo release:

Verify all external resource URLs.

Do not insert placeholder URLs such as:

example.com
fake-course.com
test-url.com


If URL cannot be verified:

remove it or use internal demo resource.


==================================================
54. DATA QUALITY RULES
==================================================

Do not use:

"Lorem ipsum"

Do not use:

"Test Course 1"

Do not use:

"Random Skill"

Do not use meaningless descriptions.


Seed data should look like real product content.


==================================================
55. CONTENT CONSISTENCY
==================================================

If resource says:

difficulty = BEGINNER

it should not require an advanced
prerequisite without a valid reason.


If resource teaches:

Model Evaluation

it should have:

Model Evaluation

in its skill mapping.


If resource requires:

Machine Learning

Machine Learning must exist.


==================================================
56. DEMO RESOURCE EXPLANATIONS
==================================================

The recommendation explanation system should
be able to generate reasons from:

skill gap
goal relevance
prerequisite fit
difficulty fit
time fit


Example:

"Model Evaluation Fundamentals is recommended
because Model Evaluation is currently one of
your largest skill gaps, its prerequisites are
satisfied, and its difficulty matches your
current learning level."


The explanation must be generated from actual
stored signals.


==================================================
57. DEMO DATA DOES NOT MEAN HARDCODED LOGIC
==================================================

Allowed:

Curated role data.

Curated skill data.

Curated dependency graph.

Curated resource catalog.

Curated assessment questions.


Not allowed:

if learner == demo:
    return this roadmap


Not allowed:

if score < 40:
    show this exact hardcoded page


Business rules must operate on the data.


==================================================
58. RESET DATA
==================================================

Provide:

scripts/reset_demo.py

or equivalent safe development command.

It must:

remove demo learner data

and recreate it through seed logic.


Never use destructive reset commands
automatically against production.


==================================================
59. SEED COMMANDS
==================================================

Recommended:

python scripts/seed.py

python scripts/validate_seed.py

python scripts/reset_demo.py


Expected:

seed.py

→ inserts/updates catalog data


validate_seed.py

→ verifies consistency


reset_demo.py

→ resets only demo data


==================================================
60. SEED DATA TESTS
==================================================

[ ] seed runs successfully
[ ] seed is idempotent
[ ] no duplicate records
[ ] all foreign keys valid
[ ] all role requirements valid
[ ] dependency graph valid
[ ] no dependency cycles
[ ] resources mapped correctly
[ ] projects mapped correctly
[ ] assessments mapped correctly
[ ] questions mapped correctly
[ ] demo learner created correctly
[ ] demo learner has intentional skill gaps
[ ] reset works


==================================================
61. MINIMUM DATA VOLUME
==================================================

For MVP:

Roles:

1–3

Skills:

15–25

Dependencies:

15–30

Resources:

20–40

Projects:

4–8

Assessments:

5–8

Questions:

50–80


Do not increase data volume merely to make
the database look large.


==================================================
62. FUTURE ROLE SUPPORT
==================================================

The schema and seed architecture must allow
future roles such as:

Data Scientist
ML Engineer
AI Engineer
Data Analyst
Backend Engineer
Cloud Engineer


Adding a role should require:

role record
role-skill mappings
optional resources

It should NOT require rewriting the recommendation
engine.


==================================================
63. FUTURE SKILL SUPPORT
==================================================

Adding a skill should require:

skill record
optional dependencies
optional role mapping
optional resource mapping


It should NOT require hardcoded frontend changes.


==================================================
64. FINAL SEED DATA FLOW
==================================================

                  SKILLS
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       ROLES              DEPENDENCIES
          │                     │
          └──────────┬──────────┘
                     ▼
              ROLE REQUIREMENTS
                     │
                     ▼
                LEARNER STATE
                     │
                     ▼
                SKILL GAPS
                     │
                     ▼
             RESOURCE CATALOG
                     │
                     ▼
              RECOMMENDATIONS
                     │
                     ▼
                  ROADMAP
                     │
                     ▼
                ASSESSMENT
                     │
                     ▼
                 MASTERY
                     │
                     ▼
             ADAPTIVE UPDATE


==================================================
65. FINAL DEFINITION OF DONE
==================================================

[ ] Seed script exists
[ ] Seed script is idempotent
[ ] Skills exist
[ ] Primary AI/ML Engineer role exists
[ ] Role requirements exist
[ ] Skill graph exists
[ ] No dependency cycles
[ ] Resources exist
[ ] Projects exist
[ ] Assessments exist
[ ] Questions exist
[ ] Resource mappings exist
[ ] Project mappings exist
[ ] Demo learner exists optionally
[ ] Demo learner has meaningful gaps
[ ] Seed validation exists
[ ] URL validation completed
[ ] Reset command exists
[ ] Recommendation engine works against seed data
[ ] Roadmap engine works against seed data
[ ] Assessment works against seed data
[ ] Adaptive engine works against seed data


==================================================
END OF SEED_DATA_SPEC.md
==================================================