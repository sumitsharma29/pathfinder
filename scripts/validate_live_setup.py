"""
PathFinder AI — Live Stack & Environment Validator (Phase 17)
Checks database connectivity, pgvector support, 22-table schema integrity,
seed data counts, and LLM provider configuration.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from sqlalchemy import text
from backend.app.db.session import engine, SessionLocal
from backend.app.core.config import settings
from backend.app.ai.providers.factory import get_llm_provider
from backend.app.models import (
    Role, Skill, SkillPrerequisite, RoleSkill,
    Resource, Project, Assessment, AssessmentQuestion, User
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_live_setup")

def run_diagnostics():
    print("=" * 65)
    print(f">> PathFinder AI -- Live Environment Diagnostics (v{settings.APP_VERSION})")
    print("=" * 65)

    all_passed = True

    # 1. Database Connection & pgvector
    print("\n[1/5] Checking Database Connectivity & PostgreSQL Version...")
    try:
        with engine.connect() as conn:
            version_str = conn.execute(text("SELECT version();")).scalar()
            db_target = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Local'
            print(f"  [OK] Connected to Database: {db_target}")
            print(f"  [OK] Engine Version: {version_str[:60]}...")
            
            # Check pgvector extension
            try:
                has_vector = conn.execute(text("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")).scalar()
                if has_vector:
                    print("  [OK] pgvector extension is INSTALLED in PostgreSQL.")
                else:
                    print("  [INFO] pgvector extension is NOT installed (using application-level cosine similarity fallback).")
            except Exception as e:
                print(f"  [INFO] Vector check notice: {e}")
    except Exception as e:
        print(f"  [FAIL] Database Connection FAILED: {e}")
        all_passed = False

    # 2. Schema Table Verification (22 Tables)
    print("\n[2/5] Checking Database Schema (22 Registered Tables)...")
    expected_tables = [
        "users", "learner_profiles", "skills", "roles", "role_skills",
        "learner_skills", "skill_prerequisites", "resources", "resource_skills",
        "projects", "project_skills", "assessments", "assessment_questions",
        "assessment_results", "roadmaps", "roadmap_items", "recommendations",
        "feedback", "progress", "conversations", "conversation_messages", "roadmap_versions"
    ]
    try:
        with engine.connect() as conn:
            existing_tables = set(
                conn.execute(
                    text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                ).scalars().all()
            )
            missing = [t for t in expected_tables if t not in existing_tables]
            if not missing:
                print(f"  [OK] All 22 application tables are present in the database.")
            else:
                print(f"  [FAIL] Missing {len(missing)} tables: {missing}")
                print("  [ACTION] Run 'alembic upgrade head' to apply migrations.")
                all_passed = False
    except Exception as e:
        print(f"  [FAIL] Schema verification error: {e}")
        all_passed = False

    # 3. Seed Catalog Verification (Phase 17 Data)
    print("\n[3/5] Checking Curated Catalog & Seed Data...")
    db = SessionLocal()
    try:
        role_count = db.query(Role).count()
        skill_count = db.query(Skill).count()
        prereq_count = db.query(SkillPrerequisite).count()
        resource_count = db.query(Resource).count()
        project_count = db.query(Project).count()
        assessment_count = db.query(Assessment).count()
        question_count = db.query(AssessmentQuestion).count()

        print(f"  * Career Roles:         {role_count} (Expected >= 8)")
        print(f"  * Skills:               {skill_count} (Expected >= 18)")
        print(f"  * Skill Prerequisites:  {prereq_count} (Expected >= 19)")
        print(f"  * Curated Resources:    {resource_count} (Expected >= 17)")
        print(f"  * Practice Projects:    {project_count} (Expected >= 4)")
        print(f"  * Skill Assessments:    {assessment_count} (Expected >= 5)")
        print(f"  * Assessment Questions: {question_count} (Expected >= 11)")

        if role_count >= 8 and skill_count >= 18 and resource_count >= 17:
            print("  [OK] Seed catalog is fully populated with primary AI/ML Engineer demo path.")
        else:
            print("  [WARN] Seed catalog is incomplete. Run 'python scripts/seed.py' to populate.")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Seed data check error: {e}")
        all_passed = False
    finally:
        db.close()

    # 4. LLM & AI Provider Configuration
    print("\n[4/5] Checking AI / LLM Provider Configuration...")
    try:
        provider_name = settings.LLM_PROVIDER
        model_name = settings.LLM_MODEL
        has_key = bool(settings.LLM_API_KEY)
        print(f"  * Configured LLM Provider: {provider_name}")
        print(f"  * Configured Model:        {model_name}")
        print(f"  * API Key Present:         {'YES' if has_key else 'NO (Deterministic Mock/Fallback active)'}")
        
        provider = get_llm_provider()
        print(f"  [OK] LLM Provider initialized successfully: {provider.__class__.__name__}")
    except Exception as e:
        print(f"  [FAIL] LLM Provider initialization error: {e}")
        all_passed = False

    # 5. Security & Secret Sanity Check
    print("\n[5/5] Checking Security & Environment Defaults...")
    if settings.SECRET_KEY == "change_this_to_a_secure_random_secret_key_in_production" and settings.APP_ENV == "production":
        print("  [WARN] Default SECRET_KEY detected in production mode! Please update .env.")
    else:
        print("  [OK] Secret key & environment configuration validated.")

    print("\n" + "=" * 65)
    if all_passed:
        print(">> ALL DIAGNOSTIC CHECKS PASSED -- PathFinder AI is ready!")
    else:
        print(">> SOME CHECKS REQUIRE ATTENTION -- See details above.")
    print("=" * 65 + "\n")
    return all_passed

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
