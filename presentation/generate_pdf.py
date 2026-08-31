"""
PathFinder Nexus — PDF Presentation Generator
Generates a 16:9 landscape, high-resolution dark-themed PDF presentation slide deck.
"""
import os
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# 16:9 Landscape Dimensions (13.33 x 7.5 inches = 960 x 540 pt)
PAGE_WIDTH = 960
PAGE_HEIGHT = 540

# Color Palette
BG_COLOR = HexColor("#020617")        # Slate-950
CARD_BG = HexColor("#0f172a")         # Slate-900
BORDER_COLOR = HexColor("#1e293b")    # Slate-800
CYAN = HexColor("#06b6d4")            # Cyan-500
EMERALD = HexColor("#10b981")         # Emerald-500
TEAL = HexColor("#14b8a6")            # Teal-500
WHITE = HexColor("#f8fafc")           # Slate-50
SLATE_LIGHT = HexColor("#cbd5e1")     # Slate-300
SLATE_MUTED = HexColor("#94a3b8")     # Slate-400
ROSE = HexColor("#f43f5e")            # Rose-500
AMBER = HexColor("#f59e0b")           # Amber-500


def draw_background(c):
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)


def draw_header(c, tag, title, tag_color=CYAN):
    # Top Tag
    c.setFillColor(tag_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, PAGE_HEIGHT - 40, tag.upper())

    # Main Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, PAGE_HEIGHT - 68, title)

    # Top accent rule
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(1)
    c.line(50, PAGE_HEIGHT - 80, PAGE_WIDTH - 50, PAGE_HEIGHT - 80)


def draw_card(c, x, y, w, h, border_color=BORDER_COLOR, fill_color=CARD_BG, line_width=1):
    c.setFillColor(fill_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)


def generate_pdf():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(output_dir, "PathFinder_Nexus_Project_Presentation.pdf")
    c = canvas.Canvas(pdf_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # ==========================================================
    # SLIDE 1: Title Slide
    # ==========================================================
    draw_background(c)
    draw_card(c, 100, 70, 760, 400, border_color=CYAN, line_width=2)

    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, 410, "FULL-STACK CAPSTONE PROJECT DEFENSE")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_WIDTH / 2, 350, "PathFinder Nexus")

    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH / 2, 310, "Autonomous, Dependency-Aware & Continuously Adaptive Learning Navigator")

    c.setStrokeColor(BORDER_COLOR)
    c.line(160, 270, 800, 270)

    c.setFillColor(EMERALD)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(PAGE_WIDTH / 2, 230, "FastAPI (Python 3.12) • PostgreSQL 16 & pgvector • React 18 SPA • Google Gemini LLM")

    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 11)
    c.drawCentredString(PAGE_WIDTH / 2, 195, "162 Backend Unit & Integration Tests (100% Deterministic Fallback)")
    c.drawCentredString(PAGE_WIDTH / 2, 165, "Topological Kahn's DAG Engine • 6-Factor Recommendation • Bayesian Evidence Fusion")

    c.showPage()

    # ==========================================================
    # SLIDE 2: Problem Statement
    # ==========================================================
    draw_background(c)
    draw_header(c, "01 / The Core Problem", "Why Modern Online Education Fails Learners", ROSE)

    cards = [
        ("01", "Linear, Static Playlists", "Courses assume identical starting baselines, forcing experts through basics and abandoning beginners when advanced prerequisites are skipped.", ROSE),
        ("02", "Hallucinating AI Chatbots", "Generic LLMs invent fake URLs, fabricate invalid course sequences, and lack relational database grounding and dependency validation.", AMBER),
        ("03", "Zero Adaptive Feedback", "When learners fail quizzes, static platforms do not dynamically restructure roadmaps or deliver prerequisite refresher interventions.", CYAN),
    ]

    for i, (num, title, desc, color) in enumerate(cards):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(x + 20, 390, num)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(x + 20, 350, title)

        c.setFillColor(SLATE_MUTED)
        c.setFont("Helvetica", 11)
        
        # Wrapped text lines
        lines = [
            desc[:40],
            desc[40:80] if len(desc) > 40 else "",
            desc[80:120] if len(desc) > 80 else "",
            desc[120:160] if len(desc) > 120 else "",
            desc[160:200] if len(desc) > 160 else "",
        ]
        y_text = 300
        for l in lines:
            if l:
                c.drawString(x + 20, y_text, l.strip())
                y_text -= 18

    c.showPage()

    # ==========================================================
    # SLIDE 3: Architectural Creed
    # ==========================================================
    draw_background(c)
    draw_header(c, "02 / Architectural Philosophy", "The PathFinder Nexus Architectural Creed", CYAN)

    draw_card(c, 50, 290, 860, 140, border_color=CYAN, line_width=2)
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2, 365, "“RAG retrieves. LLMs explain. The Database grounds. Deterministic engines decide.”")
    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH / 2, 330, "A strict architectural separation of concerns preventing AI hallucinations and ensuring mathematical integrity.")

    pillars = [
        ("RAG (pgvector)", "Retrieves verified educational resources via 1536-dim cosine similarity.", CYAN),
        ("LLM (Gemini)", "Synthesizes clear explanations, goal summaries, and interactive tutor answers.", TEAL),
        ("Database (Postgres)", "Authoritative single source of truth for roles, skills, questions, and roadmaps.", EMERALD),
        ("Deterministic Engines", "Topological Kahn DAG, 6-factor ranking, and Bayesian evidence fusion.", WHITE),
    ]

    for i, (title, desc, color) in enumerate(pillars):
        x = 50 + i * 220
        draw_card(c, x, 70, 205, 190, border_color=BORDER_COLOR)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 15, 225, title)
        c.setFillColor(SLATE_MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(x + 15, 185, desc[:28])
        c.drawString(x + 15, 165, desc[28:56])
        c.drawString(x + 15, 145, desc[56:85] if len(desc) > 56 else "")

    c.showPage()

    # ==========================================================
    # SLIDE 4: System Architecture
    # ==========================================================
    draw_background(c)
    draw_header(c, "03 / System Blueprint", "Modular Monolith Architecture & Technology Stack", EMERALD)

    layers = [
        ("1. Frontend Client (SPA)", [
            "React 18 + TypeScript + Vite",
            "Tailwind CSS Dark Theme & Glassmorphism",
            "Client-Side JWT Auth with persistence",
            "Netlify Edge CDN Deployment"
        ], CYAN),
        ("2. FastAPI Backend Core", [
            "Python 3.12 Modular Monolith",
            "Clean Architecture (Routers/Services/Repos)",
            "Argon2id Password Security + Correlation IDs",
            "Render Cloud Web Service (Uvicorn)"
        ], EMERALD),
        ("3. Data & AI Layer", [
            "PostgreSQL 16 with pgvector Extension",
            "22 Normalized Relational Entity Tables",
            "Google Gemini 1.5/2.0 Flash + OpenAI Embeddings",
            "Deterministic Mock Fallback Provider"
        ], TEAL),
    ]

    for i, (title, items, color) in enumerate(layers):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 20, 395, title)

        c.setFillColor(SLATE_LIGHT)
        c.setFont("Helvetica", 11)
        y_i = 350
        for item in items:
            c.drawString(x + 20, y_i, f"• {item[:32]}")
            if len(item) > 32:
                y_i -= 14
                c.drawString(x + 28, y_i, item[32:])
            y_i -= 28

    c.showPage()

    # ==========================================================
    # SLIDE 5: Engine 1 — AI Goal Extraction
    # ==========================================================
    draw_background(c)
    draw_header(c, "04 / Engine 1", "AI Goal Understanding & Grounded Extraction", CYAN)

    draw_card(c, 50, 80, 415, 360, border_color=CYAN)
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 395, "Natural Language Input:")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(70, 365, "“I want to become an AI Engineer specializing in LLMs &")
    c.drawString(70, 345, "RAG systems within 12 weeks with 2 hours daily study.”")

    c.setFillColor(EMERALD)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 290, "Structured Pydantic Extraction:")
    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 11)
    c.drawString(70, 255, "• Target Role: AI/ML Engineer (Matched)")
    c.drawString(70, 230, "• Target Duration: 12 Weeks")
    c.drawString(70, 205, "• Daily Study: 2.0 Hours")
    c.drawString(70, 180, "• Extracted Skills: Python (40%), LLMs (0%), Vector DBs (0%)")

    draw_card(c, 495, 80, 415, 360, border_color=BORDER_COLOR)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(515, 395, "Canonical Role Grounding Pipeline:")
    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 11)
    steps = [
        "1. Raw Prompt Sanitization & XML Delimiter Tagging",
        "2. Gemini Structured JSON Mode with Pydantic Validation",
        "3. Database Lookup: Matches against 10 Canonical Roles",
        "4. Ambiguity Handler: Returns suggested roles if unresolved",
        "5. Zero Hallucinations: Non-existent roles never persisted"
    ]
    y_s = 350
    for s in steps:
        c.drawString(515, y_s, s)
        y_s -= 35

    c.showPage()

    # ==========================================================
    # SLIDE 6: Engine 2 — Dynamic Skill Gap
    # ==========================================================
    draw_background(c)
    draw_header(c, "05 / Engine 2", "Dynamic Skill Gap & Role Readiness Engine", EMERALD)

    items_gap = [
        ("Zero Static Storage", "Skill gaps are computed on-the-fly dynamically upon query. Eliminates stale cached tables and guarantees synchronization.", CYAN),
        ("Gap Formulation", "Gap = max(Required - LearnerProficiency, 0)\nStrictly non-negative delta for every skill required by role.", EMERALD),
        ("Role Readiness Score", "Readiness = (Σ Current_w / Σ Required_w) × 100\nWeighted importance factor ensures critical skills drive readiness.", TEAL),
    ]

    for i, (title, desc, color) in enumerate(items_gap):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 20, 395, title)

        c.setFillColor(SLATE_LIGHT)
        c.setFont("Helvetica", 11)
        y_g = 350
        for l in desc.split("\n"):
            c.drawString(x + 20, y_g, l[:34])
            if len(l) > 34:
                y_g -= 16
                c.drawString(x + 20, y_g, l[34:])
            y_g -= 25

    c.showPage()

    # ==========================================================
    # SLIDE 7: Engine 3 — Kahn's DAG
    # ==========================================================
    draw_background(c)
    draw_header(c, "06 / Engine 3", "Topological Roadmap Engine (Kahn's DAG Algorithm)", TEAL)

    draw_card(c, 50, 80, 415, 360, border_color=TEAL)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 395, "Prerequisite-Aware Directed Acyclic Graph")
    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 11)
    c.drawString(70, 350, "• Strict in-degree topological sort")
    c.drawString(70, 320, "• Guarantees prerequisites precede advanced topics")
    c.drawString(70, 290, "• Cycle detection prevents circular dependencies")
    c.drawString(70, 260, "• Dynamic milestone unlocking based on mastery")

    draw_card(c, 495, 80, 415, 360, border_color=BORDER_COLOR)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(515, 395, "Kahn's Execution Workflow:")
    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 11)
    k_steps = [
        "1. Calculate in-degree for all required role skills",
        "2. Initialize queue with all in-degree == 0 nodes",
        "3. Pop node u -> append to roadmap sequence",
        "4. Decrement in-degree for outgoing neighbors v",
        "5. If in-degree[v] == 0, push v to queue",
        "6. Assign milestone sequence & estimated weeks"
    ]
    y_k = 350
    for ks in k_steps:
        c.drawString(515, y_k, ks)
        y_k -= 30

    c.showPage()

    # ==========================================================
    # SLIDE 8: Engine 4 — 6-Factor Recommendation
    # ==========================================================
    draw_background(c)
    draw_header(c, "07 / Engine 4", "Normalized 6-Factor Explainable Recommendation", CYAN)

    draw_card(c, 50, 350, 860, 80, border_color=CYAN, line_width=1.5)
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_WIDTH / 2, 395, "Score = 0.30(Gap) + 0.20(Prereq) + 0.15(Goal) + 0.15(Diff) + 0.10(Time) + 0.10(Pref)")
    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_WIDTH / 2, 370, "Multi-objective normalized scoring where all weight coefficients sum strictly to 1.0.")

    factors = [
        ("30%", "Skill Gap Weight", "Prioritizes biggest skill gaps", CYAN),
        ("20%", "Prereq Readiness", "Ensures learner is ready", TEAL),
        ("15%", "Goal Alignment", "Matches target role curriculum", EMERALD),
        ("15%", "Difficulty Match", "Aligns with user level", WHITE),
        ("10%", "Time Investment", "Fits daily study budget", AMBER),
        ("10%", "Format Preference", "Video, article, code balance", ROSE),
    ]

    for i, (pct, title, desc, color) in enumerate(factors):
        col = i % 3
        row = i // 3
        x = 50 + col * 295
        y = 200 - row * 120
        draw_card(c, x, y, 270, 100, border_color=BORDER_COLOR)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 15, y + 65, f"{pct} — {title}")
        c.setFillColor(SLATE_MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(x + 15, y + 35, desc)

    c.showPage()

    # ==========================================================
    # SLIDE 9: Engine 5 & 6 — Assessments
    # ==========================================================
    draw_background(c)
    draw_header(c, "08 / Engine 5 & 6", "Sanitized Assessments & Bayesian Evidence Fusion", EMERALD)

    draw_card(c, 50, 80, 415, 360, border_color=CYAN)
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 395, "Anti-Cheat Sanitized Delivery")
    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 11)
    c.drawString(70, 350, "• Correct answers NEVER sent to browser client")
    c.drawString(70, 320, "• Client receives only question IDs & option keys")
    c.drawString(70, 290, "• 100% Authoritative Server-Side Grading")
    c.drawString(70, 260, "• Eliminates browser inspect element cheat exploits")

    draw_card(c, 495, 80, 415, 360, border_color=EMERALD)
    c.setFillColor(EMERALD)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(515, 395, "Bayesian Evidence Fusion Formula:")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(515, 350, "P_new = round(0.30 × P_old + 0.70 × Score, 2)")
    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 11)
    c.drawString(515, 305, "• Prevents single-test score volatility")
    c.drawString(515, 275, "• Mastery Thresholds:")
    c.drawString(530, 250, "→ Mastered: Score ≥ 80%")
    c.drawString(530, 225, "→ In Progress: 60% ≤ Score < 80%")
    c.drawString(530, 200, "→ Critical Deficiency: Score < 60%")

    c.showPage()

    # ==========================================================
    # SLIDE 10: Adaptive Interventions
    # ==========================================================
    draw_background(c)
    draw_header(c, "09 / Adaptive Core", "Closed-Loop Adaptive Interventions & Next Best Action", AMBER)

    tiers = [
        ("Score < 40%", "Foundational Lock", "Locks dependent roadmap items, inserts prerequisite refresher resources, and updates Next Best Action.", ROSE),
        ("40% ≤ Score < 80%", "Targeted Reinforce", "Delivers focused practice problems while keeping milestone active for revision.", AMBER),
        ("Score ≥ 80%", "Milestone Mastery", "Marks milestone completed, updates topological graph, and unlocks downstream milestones.", EMERALD),
    ]

    for i, (tag, title, desc, color) in enumerate(tiers):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 20, 395, tag)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x + 20, 365, title)

        c.setFillColor(SLATE_MUTED)
        c.setFont("Helvetica", 11)
        y_t = 320
        for l in [desc[:36], desc[36:72], desc[72:110], desc[110:]]:
            if l:
                c.drawString(x + 20, y_t, l.strip())
                y_t -= 18

    c.showPage()

    # ==========================================================
    # SLIDE 11: Grounded RAG Assistant
    # ==========================================================
    draw_background(c)
    draw_header(c, "10 / Engine 7", "Grounded RAG Knowledge Assistant & Citation Safety", CYAN)

    draw_card(c, 50, 80, 415, 360, border_color=CYAN)
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 395, "pgvector Semantic Search")
    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica", 11)
    c.drawString(70, 350, "• 1536-dimensional OpenAI vector embeddings")
    c.drawString(70, 320, "• Cosine similarity threshold cutoff (≥ 0.50)")
    c.drawString(70, 290, "• Top-K semantic context retrieval from Postgres")

    draw_card(c, 495, 80, 415, 360, border_color=EMERALD)
    c.setFillColor(EMERALD)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(515, 395, "Anti-Hallucination Guardrails")
    c.setFillColor(SLATE_MUTED)
    c.setFont("Helvetica", 11)
    c.drawString(515, 350, "• Strict XML security delimiters protect context")
    c.drawString(515, 320, "• Every answer cites validated database resource URLs")
    c.drawString(515, 290, "• Zero-context fallback refuses to fabricate URLs")

    c.showPage()

    # ==========================================================
    # SLIDE 12: Database Schema
    # ==========================================================
    draw_background(c)
    draw_header(c, "11 / Data Foundation", "Relational Database Schema (22 Core Tables)", EMERALD)

    db_groups = [
        ("Auth & Users", "users\nlearner_profiles\nlearner_skills\nuser_preferences", CYAN),
        ("Catalog & Graph", "roles\nskills\nskill_prerequisites\nrole_skills", TEAL),
        ("Roadmaps & Content", "roadmaps\nroadmap_items\nresources\nprojects", EMERALD),
        ("Assess & Chat", "assessments\nassessment_questions\nsubmissions\nchat_messages", WHITE),
    ]

    for i, (title, tables, color) in enumerate(db_groups):
        x = 50 + i * 220
        draw_card(c, x, 80, 205, 360, border_color=BORDER_COLOR)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 15, 395, title)

        c.setFillColor(SLATE_LIGHT)
        c.setFont("Helvetica", 11)
        y_db = 350
        for t in tables.split("\n"):
            c.drawString(x + 15, y_db, f"• {t}")
            y_db -= 28

    c.showPage()

    # ==========================================================
    # SLIDE 13: Testing & Quality Metrics
    # ==========================================================
    draw_background(c)
    draw_header(c, "12 / Verification", "Automated Testing & Benchmark Results", TEAL)

    test_cards = [
        ("162 Tests", "Backend Pytest Suite", "100% passing across auth, DAG roadmaps, recommendations, evidence fusion, and security.", EMERALD),
        ("0 Errors", "TypeScript Strict Build", "Zero TypeScript compilation errors with optimized Vite production bundle.", CYAN),
        ("100% Safe", "Deterministic Fallback", "System operates smoothly even when cloud AI rate limits hit or in offline mode.", TEAL),
    ]

    for i, (stat, title, desc, color) in enumerate(test_cards):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(x + 20, 395, stat)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(x + 20, 350, title)

        c.setFillColor(SLATE_MUTED)
        c.setFont("Helvetica", 11)
        y_v = 300
        for l in [desc[:36], desc[36:72], desc[72:]]:
            if l:
                c.drawString(x + 20, y_v, l.strip())
                y_v -= 18

    c.showPage()

    # ==========================================================
    # SLIDE 14: Cloud Deployment Architecture
    # ==========================================================
    draw_background(c)
    draw_header(c, "13 / Deployment", "Production Cloud Deployment Architecture", CYAN)

    deploy_tiers = [
        ("Frontend: Netlify", [
            "React 18 SPA on Global Edge CDN",
            "Automated netlify.toml headers & caching",
            "_redirects file for SPA client-side deep linking",
            "Command: npm run build"
        ], CYAN),
        ("Backend: Render", [
            "FastAPI Web Service running Uvicorn",
            "render.yaml blueprint configuration",
            "Dynamic CORS regex matching Netlify previews",
            "Health Check Probes: /health & /health/ready"
        ], EMERALD),
        ("Database: PostgreSQL", [
            "Cloud PostgreSQL 16 Instance",
            "Automated migrations via deploy_init.py",
            "Idempotent catalog seeding on startup",
            "pgvector similarity indexing"
        ], TEAL),
    ]

    for i, (title, items, color) in enumerate(deploy_tiers):
        x = 50 + i * 295
        draw_card(c, x, 80, 270, 360, border_color=color, line_width=1.5)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 20, 395, title)

        c.setFillColor(SLATE_LIGHT)
        c.setFont("Helvetica", 11)
        y_d = 350
        for item in items:
            c.drawString(x + 20, y_d, f"• {item[:32]}")
            if len(item) > 32:
                y_d -= 14
                c.drawString(x + 28, y_d, item[32:])
            y_d -= 26

    c.showPage()

    # ==========================================================
    # SLIDE 15: Conclusion
    # ==========================================================
    draw_background(c)
    draw_card(c, 100, 70, 760, 400, border_color=EMERALD, line_width=2)

    c.setFillColor(EMERALD)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, 410, "CONCLUSION & PROJECT DEFENSE")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(PAGE_WIDTH / 2, 355, "PathFinder Nexus")

    c.setFillColor(CYAN)
    c.setFont("Helvetica-Oblique", 15)
    c.drawCentredString(PAGE_WIDTH / 2, 315, "“Transforming natural-language ambition into deterministic, adaptive mastery.”")

    c.setStrokeColor(BORDER_COLOR)
    c.line(160, 270, 800, 270)

    c.setFillColor(SLATE_LIGHT)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(PAGE_WIDTH / 2, 230, "✓ 7 Fully Integrated Engines  |  ✓ 162 Passed Tests  |  ✓ Production Deployment-Ready")

    c.setFillColor(TEAL)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_WIDTH / 2, 175, "Thank you! We are ready for live demonstration & questions.")

    c.save()
    print(f"[SUCCESS] PDF Presentation successfully created: {pdf_path}")


if __name__ == "__main__":
    generate_pdf()
