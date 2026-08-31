"""Deployment initialization script for PathFinder Nexus.
Executes database migrations and idempotent catalog seed data on cloud deployments (e.g. Render, Supabase, Neon).
"""
import os
import sys

# Ensure root directory is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.app.db.session import engine, Base
from backend.app.core.config import settings
from scripts.seed import seed_database


def run_deployment_init():
    print("[INIT] Starting PathFinder Nexus Deployment Initializer...")
    print(f"[INFO] Environment: {settings.APP_ENV} | App: {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        print("[INFO] Testing Database Connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[SUCCESS] Database connection established.")

        print("[INFO] Creating database schema tables...")
        # Import all models to ensure metadata is populated
        import backend.app.models
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database schema synchronized.")

        print("[INFO] Seeding canonical catalog data...")
        seed_database()
        print("[SUCCESS] Seed verification complete.")
        print("[SUCCESS] Deployment Initialization Succeeded!")
        return 0
    except Exception as e:
        print(f"[WARN] Deployment init encountered a database warning/error: {e}")
        print("[INFO] If database is not configured yet or cloud DB is starting, application will start in fallback mode.")
        return 0


if __name__ == "__main__":
    sys.exit(run_deployment_init())
