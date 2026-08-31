# PathFinder Nexus — Project Presentation & Architectural Defense

> **Autonomous, Dependency-Aware & Continuously Adaptive Learning Navigation Platform**
> *Full-Stack Capstone Project • Production Ready*

---

## Slide 1: Executive Summary & Vision

### What is PathFinder Nexus?
PathFinder Nexus is an intelligent, dependency-aware, explainable, and continuously adaptive career navigation engine. It translates a learner's free-form natural language ambitions into a mathematically structured topological learning roadmap, backed by grounded resources, server-graded assessments, and dynamic interventions.

### Key Metrics
- **Stack**: FastAPI (Python 3.12) + PostgreSQL 16 & pgvector + React 18 + Google Gemini LLM
- **Test Suite**: 162 Unit & Integration Backend Tests Passing (100% Deterministic Fallback)
- **Engines**: 7 Independent Deterministic & AI Subsystems
- **Deployments**: Netlify (Frontend SPA) + Render (FastAPI Web Service + Postgres)

---

## Slide 2: The Core Problem in Modern EdTech

1. **Static, Linear Playlists**:
   - Courses assume identical starting knowledge for all students.
   - Experts get bored with basics; beginners drop out due to unfulfilled prerequisites.
2. **Hallucination-Prone AI Chatbots**:
   - Generic chatbots invent fake URLs, fabricate invalid curricula, and have no database grounding.
3. **No Closed-Loop Adaptation**:
   - When a user fails a quiz, static platforms do not restructure the learning path or provide foundational interventions.

---

## Slide 3: The Architectural Creed

> **"RAG retrieves. LLMs explain. The Database grounds. Deterministic engines decide."**

```
 ┌────────────────┐       ┌───────────────────────┐       ┌──────────────────────┐
 │  RAG (pgvector)│ ────► │ LLM (Google Gemini)   │ ────► │ Database (Grounding) │
 └────────────────┘       └───────────────────────┘       └──────────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │     Deterministic Engines     │
                     │ (Kahn DAG, 6-Factor, Fusion)  │
                     └───────────────────────────────┘
```

---

## Slide 4: The 7 Core Subsystems & Algorithms

### 1. AI Goal Understanding Engine
- Analyzes natural-language career aspirations (e.g. *"I want to become an AI Engineer specializing in LLMs in 12 weeks with 2 hours daily"*).
- Uses Gemini with structured Pydantic extraction to match canonical database roles and identify prior skills.

### 2. Dynamic Skill Gap Engine
- Deterministically computes skill proficiencies, gaps, and readiness in real time with zero static table persistence:
  $$\text{Gap} = \max(\text{RequiredProficiency} - \text{LearnerProficiency}, 0)$$
- Computes weighted Role Readiness:
  $$R = \left(\frac{\sum (\text{Current}_i \times W_i)}{\sum (\text{Required}_i \times W_i)}\right) \times 100$$

### 3. Topological Roadmap Engine (Kahn's Algorithm)
- Constructs prerequisite-aware Directed Acyclic Graphs (DAGs).
- Guarantees that prerequisite skills (e.g. *Python Fundamentals*) strictly precede dependent milestones (e.g. *PyTorch & Neural Networks*).

### 4. Normalized 6-Factor Recommendation Engine
- Ranks resources across 6 normalized objectives summing strictly to 1.0:
  $$\text{Score} = 0.30 G + 0.20 P + 0.15 R + 0.15 D + 0.10 T + 0.10 L$$
  *(Gap 30%, Prereqs 20%, Goal 15%, Difficulty 15%, Time 10%, Preference 10%)*

### 5. Server-Graded Assessment Engine
- Anti-cheat sanitized question delivery: correct answers and explanations are never sent to the browser before submission.
- Authoritative backend scoring.

### 6. Evidence Fusion & Closed-Loop Adaptive Interventions
- Bayesian-inspired proficiency updates:
  $$P_{\text{new}} = \text{round}(0.30 \times P_{\text{old}} + 0.70 \times \text{Score}, 2)$$
- Score $< 40\%$: Triggers foundational interventions and locks downstream prerequisites.
- Score $\ge 80\%$: Unlocks advanced topological milestones.

### 7. Grounded RAG Knowledge Assistant
- Semantic pgvector similarity search over curated database resources.
- XML security delimiter isolation and anti-hallucination source citation verification.

---

## Slide 5: System Architecture & Deployment

- **Frontend (Netlify)**:
  - React 18 + Vite + Tailwind CSS Dark Mode
  - `netlify.toml` + `public/_redirects` for SPA deep link routing
  - Dynamic `VITE_API_URL` environment configuration
- **Backend (Render)**:
  - FastAPI Modular Monolith + Uvicorn
  - `render.yaml` blueprint with health check (`/health`)
  - Dynamic CORS regex supporting Netlify domains
- **Database (PostgreSQL + pgvector)**:
  - 22 Relational Tables (Users, Catalog, Roadmaps, Milestones, Assessments, Chat)
  - Auto-initialization with `scripts/deploy_init.py`

---

## Slide 6: Verification & Quality Assurance

- **162 Backend Pytest Tests**: 100% passing across auth, catalogs, DAG roadmaps, assessments, RAG, and security.
- **Zero Frontend TypeScript Errors**: Strict production build via `npm run build`.
- **100% Offline Resiliency**: Deterministic mock provider activates smoothly if cloud AI credentials are not provided.

---

## Slide 7: Live Demonstration & Evaluation

- **Interactive Presentation Deck**: Open `/docs/presentation.html` in any browser.
- **Live App**: Register -> AI Goal Extraction -> Interactive DAG Roadmap -> Server Graded Assessment -> Dynamic Recalibration -> Grounded RAG Assistant.
