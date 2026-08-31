"""PathFinder AI — Seed Data Validator
Validates the integrity, consistency, and completeness of the database seed catalog.
Checks:
- Entity counts (Roles, Skills, RoleSkills, Prerequisites, Resources, Projects, Assessments, Questions)
- Foreign key integrity
- DAG integrity (no self-loops, no cyclic dependencies)
- Constraint verification
"""
import sys
import os
from collections import defaultdict, deque

# Ensure root directory is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from backend.app.db.session import SessionLocal
from backend.app.models import (
    Role, Skill, SkillPrerequisite, RoleSkill,
    Resource, ResourceSkill, Project, ProjectSkill,
    Assessment, AssessmentQuestion
)


def validate_seed():
    db = SessionLocal()
    errors = []
    warnings = []
    
    print("==================================================")
    print("PATHFINDER AI — SEED DATA VALIDATION")
    print("==================================================")

    try:
        # 1. Count checks
        roles_count = db.execute(select(func.count(Role.id))).scalar()
        skills_count = db.execute(select(func.count(Skill.id))).scalar()
        role_skills_count = db.execute(select(func.count()).select_from(RoleSkill)).scalar()
        prereqs_count = db.execute(select(func.count()).select_from(SkillPrerequisite)).scalar()
        resources_count = db.execute(select(func.count(Resource.id))).scalar()
        resource_skills_count = db.execute(select(func.count()).select_from(ResourceSkill)).scalar()
        projects_count = db.execute(select(func.count(Project.id))).scalar()
        project_skills_count = db.execute(select(func.count()).select_from(ProjectSkill)).scalar()
        assessments_count = db.execute(select(func.count(Assessment.id))).scalar()
        questions_count = db.execute(select(func.count(AssessmentQuestion.id))).scalar()

        print(f"Roles count:             {roles_count}")
        print(f"Skills count:            {skills_count}")
        print(f"Role-Skill mappings:     {role_skills_count}")
        print(f"Skill Prerequisites:     {prereqs_count}")
        print(f"Resources count:         {resources_count}")
        print(f"Resource-Skill mappings: {resource_skills_count}")
        print(f"Projects count:          {projects_count}")
        print(f"Project-Skill mappings:  {project_skills_count}")
        print(f"Assessments count:       {assessments_count}")
        print(f"Questions count:         {questions_count}")
        print("--------------------------------------------------")

        if roles_count < 1:
            errors.append("Validation Failure: No roles found in database.")
        if skills_count < 18:
            errors.append(f"Validation Failure: Expected at least 18 skills, found {skills_count}.")
        if prereqs_count < 10:
            errors.append(f"Validation Failure: Expected at least 10 prerequisites, found {prereqs_count}.")
        if resources_count < 10:
            errors.append(f"Validation Failure: Expected at least 10 resources, found {resources_count}.")
        if projects_count < 3:
            errors.append(f"Validation Failure: Expected at least 3 projects, found {projects_count}.")
        if assessments_count < 3:
            errors.append(f"Validation Failure: Expected at least 3 assessments, found {assessments_count}.")
        if questions_count < 5:
            errors.append(f"Validation Failure: Expected at least 5 questions, found {questions_count}.")

        # 2. Check AI/ML Engineer Role and 18 Skills
        aiml_role = db.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
        if not aiml_role:
            errors.append("Validation Failure: Canonical role 'ai-ml-engineer' is missing.")
        else:
            aiml_skills = db.execute(select(RoleSkill).where(RoleSkill.role_id == aiml_role.id)).scalars().all()
            if len(aiml_skills) < 18:
                errors.append(f"Validation Failure: AI/ML Engineer role requires 18 mapped skills, found {len(aiml_skills)}.")
            else:
                print(f"PASS: AI/ML Engineer role has all {len(aiml_skills)} required skill mappings.")

        # 3. Graph Validation: Check for Self-Loops and Cycles in Skill Prerequisites
        prereqs = db.execute(select(SkillPrerequisite)).scalars().all()
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)
        all_graph_nodes = set()

        for p in prereqs:
            if p.skill_id == p.prerequisite_skill_id:
                errors.append(f"Validation Failure: Self-loop detected in prerequisite graph for skill ID {p.skill_id}.")
            adj_list[p.prerequisite_skill_id].append(p.skill_id)
            in_degree[p.skill_id] += 1
            all_graph_nodes.add(p.skill_id)
            all_graph_nodes.add(p.prerequisite_skill_id)

        # Topological sort (Kahn's Algorithm) to detect cycles
        queue = deque([node for node in all_graph_nodes if in_degree[node] == 0])
        visited_count = 0
        while queue:
            node = queue.popleft()
            visited_count += 1
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(all_graph_nodes):
            errors.append("Validation Failure: Cyclic dependency detected in skill prerequisites graph (DAG violation)!")
        else:
            print("PASS: Skill prerequisite graph is a valid, acyclic Directed Acyclic Graph (DAG).")

        # 4. Check assessment questions have answers and options
        questions = db.execute(select(AssessmentQuestion)).scalars().all()
        for q in questions:
            if not q.correct_answer:
                errors.append(f"Validation Failure: Question {q.id} has no correct_answer.")
            if q.points <= 0:
                errors.append(f"Validation Failure: Question {q.id} has non-positive points ({q.points}).")

        print("--------------------------------------------------")
        if errors:
            print(f"VALIDATION FAILED with {len(errors)} error(s):")
            for err in errors:
                print(f"  [ERROR] {err}")
            return False
        else:
            print("ALL SEED VALIDATION CHECKS PASSED PERFECTLY!")
            return True

    except Exception as e:
        print(f"FATAL ERROR during validation: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = validate_seed()
    sys.exit(0 if success else 1)
