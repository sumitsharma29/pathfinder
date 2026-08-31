"""PathFinder AI — Database Seed Script
Populates the canonical catalog (Roles, Skills, Prerequisites, Role-Skills, Resources,
Resource-Skills, Projects, Project-Skills, Assessments, Questions).
Idempotent: Safe to run repeatedly without creating duplicate rows or overwriting user data.
"""
import sys
import os
import uuid

# Ensure root directory is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from backend.app.db.session import SessionLocal
from backend.app.models import (
    Role, Skill, SkillPrerequisite, RoleSkill,
    Resource, ResourceSkill, Project, ProjectSkill,
    Assessment, AssessmentQuestion, User, LearnerProfile,
    LearnerSkill
)
from backend.app.core.security import hash_password


def seed_database():
    db = SessionLocal()
    try:
        print("--- Starting PathFinder AI Seed Process ---")

        # ----------------------------------------------------------------------
        # 1. ROLES
        # ----------------------------------------------------------------------
        roles_data = [
            {
                "name": "AI/ML Engineer",
                "slug": "ai-ml-engineer",
                "description": "An AI/ML Engineer designs, trains, evaluates, and deploys machine learning models and intelligent systems in production."
            },
            {
                "name": "Data Scientist",
                "slug": "data-scientist",
                "description": "A Data Scientist analyzes complex datasets, builds predictive statistical models, and extracts actionable insights."
            },
            {
                "name": "Data Analyst",
                "slug": "data-analyst",
                "description": "A Data Analyst interprets data, creates dashboards, conducts exploratory analysis, and translates data into business value."
            },
            {
                "name": "Full Stack Developer",
                "slug": "full-stack-developer",
                "description": "A Full Stack Developer builds end-to-end web applications across frontend user interfaces and backend services."
            },
            {
                "name": "Backend Developer",
                "slug": "backend-developer",
                "description": "A Backend Developer creates robust APIs, microservices, databases, and core server-side application logic."
            },
            {
                "name": "Cloud Engineer",
                "slug": "cloud-engineer",
                "description": "A Cloud Engineer architectures, maintains, and scales cloud infrastructure and distributed environments."
            },
            {
                "name": "DevOps Engineer",
                "slug": "devops-engineer",
                "description": "A DevOps Engineer implements CI/CD pipelines, containerization, infrastructure-as-code, and reliability automation."
            },
            {
                "name": "Cybersecurity Analyst",
                "slug": "cybersecurity-analyst",
                "description": "A Cybersecurity Analyst assesses threats, monitors systems, conducts security audits, and secures application architectures."
            }
        ]

        roles_by_slug = {}
        for r_info in roles_data:
            role = db.execute(select(Role).where(Role.slug == r_info["slug"])).scalar_one_or_none()
            if not role:
                role = Role(
                    name=r_info["name"],
                    slug=r_info["slug"],
                    description=r_info["description"]
                )
                db.add(role)
                db.flush()
                print(f"Created Role: {role.name}")
            roles_by_slug[role.slug] = role

        # ----------------------------------------------------------------------
        # 2. SKILLS
        # ----------------------------------------------------------------------
        skills_data = [
            {"name": "Programming Fundamentals", "slug": "programming-fundamentals", "category": "Programming", "difficulty": "beginner", "estimated_hours": 20.0, "description": "Variables, loops, control structures, basic algorithmic problem solving."},
            {"name": "Python", "slug": "python", "category": "Programming", "difficulty": "beginner", "estimated_hours": 30.0, "description": "Python syntax, data structures, object-oriented concepts, and package ecosystems."},
            {"name": "SQL", "slug": "sql", "category": "Data", "difficulty": "beginner", "estimated_hours": 25.0, "description": "Relational querying, joins, aggregations, CTEs, and database querying."},
            {"name": "Probability", "slug": "probability", "category": "Mathematics", "difficulty": "intermediate", "estimated_hours": 20.0, "description": "Probability rules, conditional probability, Bayes theorem, distributions."},
            {"name": "Statistics", "slug": "statistics", "category": "Mathematics", "difficulty": "intermediate", "estimated_hours": 25.0, "description": "Descriptive statistics, hypothesis testing, variance, correlation, inference."},
            {"name": "Data Processing", "slug": "data-processing", "category": "Data", "difficulty": "intermediate", "estimated_hours": 25.0, "description": "Pandas, NumPy, data wrangling, missing data imputation, cleaning pipelines."},
            {"name": "Machine Learning", "slug": "machine-learning", "category": "Machine Learning", "difficulty": "intermediate", "estimated_hours": 40.0, "description": "Supervised & unsupervised learning, classification, regression, clustering."},
            {"name": "Model Evaluation", "slug": "model-evaluation", "category": "Machine Learning", "difficulty": "intermediate", "estimated_hours": 20.0, "description": "ROC-AUC, Precision, Recall, F1, cross-validation, bias-variance tradeoff."},
            {"name": "Feature Engineering", "slug": "feature-engineering", "category": "Machine Learning", "difficulty": "intermediate", "estimated_hours": 20.0, "description": "Feature scaling, encoding, selection, polynomial features, dimensionality reduction."},
            {"name": "Deep Learning", "slug": "deep-learning", "category": "Deep Learning", "difficulty": "advanced", "estimated_hours": 45.0, "description": "Artificial neural networks, backpropagation, CNNs, RNNs, PyTorch/TensorFlow."},
            {"name": "NLP", "slug": "nlp", "category": "AI", "difficulty": "advanced", "estimated_hours": 30.0, "description": "Tokenization, word embeddings, transformer architectures, sequence modeling."},
            {"name": "Computer Vision", "slug": "computer-vision", "category": "AI", "difficulty": "advanced", "estimated_hours": 30.0, "description": "Image filtering, convolutional networks, object detection, segmentation."},
            {"name": "Generative AI", "slug": "generative-ai", "category": "AI", "difficulty": "advanced", "estimated_hours": 35.0, "description": "Large language models, prompt engineering, fine-tuning, RAG systems, agents."},
            {"name": "MLOps", "slug": "mlops", "category": "Production AI", "difficulty": "advanced", "estimated_hours": 35.0, "description": "Model serving, experiment tracking, pipeline orchestration, model monitoring."},
            {"name": "Git", "slug": "git", "category": "Developer Tools", "difficulty": "beginner", "estimated_hours": 10.0, "description": "Version control, branching, pull requests, merge conflict resolution."},
            {"name": "APIs", "slug": "apis", "category": "Backend", "difficulty": "intermediate", "estimated_hours": 20.0, "description": "REST principles, HTTP methods, status codes, FastAPI, OpenAPI integration."},
            {"name": "Docker", "slug": "docker", "category": "DevOps", "difficulty": "intermediate", "estimated_hours": 20.0, "description": "Containerization, Dockerfiles, compose multi-container environments."},
            {"name": "System Design", "slug": "system-design", "category": "Software Engineering", "difficulty": "advanced", "estimated_hours": 30.0, "description": "Scalable architectural patterns, latency, caching, database replication, load balancing."}
        ]

        skills_by_slug = {}
        for s_info in skills_data:
            skill = db.execute(select(Skill).where(Skill.slug == s_info["slug"])).scalar_one_or_none()
            if not skill:
                skill = Skill(
                    name=s_info["name"],
                    slug=s_info["slug"],
                    category=s_info["category"],
                    difficulty=s_info["difficulty"],
                    estimated_hours=s_info["estimated_hours"],
                    description=s_info["description"]
                )
                db.add(skill)
                db.flush()
                print(f"Created Skill: {skill.name}")
            skills_by_slug[skill.slug] = skill

        # ----------------------------------------------------------------------
        # 3. SKILL PREREQUISITES (DAG)
        # ----------------------------------------------------------------------
        prereqs_data = [
            ("python", "programming-fundamentals", 1.0),
            ("data-processing", "python", 1.0),
            ("data-processing", "sql", 0.8),
            ("statistics", "probability", 1.0),
            ("machine-learning", "statistics", 1.0),
            ("machine-learning", "data-processing", 1.0),
            ("model-evaluation", "machine-learning", 1.0),
            ("feature-engineering", "machine-learning", 1.0),
            ("deep-learning", "machine-learning", 1.0),
            ("generative-ai", "deep-learning", 1.0),
            ("nlp", "deep-learning", 0.8),
            ("nlp", "python", 0.8),
            ("computer-vision", "deep-learning", 0.8),
            ("computer-vision", "python", 0.8),
            ("apis", "git", 0.8),
            ("mlops", "apis", 0.8),
            ("mlops", "docker", 0.8),
            ("mlops", "git", 0.8),
            ("system-design", "apis", 0.8),
        ]

        for s_slug, p_slug, strength in prereqs_data:
            s_obj = skills_by_slug.get(s_slug)
            p_obj = skills_by_slug.get(p_slug)
            if s_obj and p_obj:
                exists = db.execute(
                    select(SkillPrerequisite).where(
                        SkillPrerequisite.skill_id == s_obj.id,
                        SkillPrerequisite.prerequisite_skill_id == p_obj.id
                    )
                ).scalar_one_or_none()
                if not exists:
                    sp = SkillPrerequisite(
                        skill_id=s_obj.id,
                        prerequisite_skill_id=p_obj.id,
                        strength=strength
                    )
                    db.add(sp)
                    print(f"Added Prerequisite: {s_obj.name} requires {p_obj.name} ({strength})")

        # ----------------------------------------------------------------------
        # 4. ROLE-SKILL REQUIREMENTS (AI/ML Engineer primary)
        # ----------------------------------------------------------------------
        aiml_role = roles_by_slug.get("ai-ml-engineer")
        if aiml_role:
            aiml_reqs = [
                ("python", 80.0, 1.0),
                ("programming-fundamentals", 70.0, 0.7),
                ("sql", 65.0, 0.8),
                ("statistics", 75.0, 0.9),
                ("probability", 70.0, 0.8),
                ("data-processing", 75.0, 0.9),
                ("machine-learning", 80.0, 1.0),
                ("model-evaluation", 75.0, 0.9),
                ("feature-engineering", 70.0, 0.8),
                ("deep-learning", 70.0, 0.9),
                ("nlp", 60.0, 0.7),
                ("computer-vision", 60.0, 0.7),
                ("generative-ai", 70.0, 0.8),
                ("mlops", 60.0, 0.8),
                ("git", 65.0, 0.7),
                ("apis", 60.0, 0.7),
                ("docker", 55.0, 0.7),
                ("system-design", 50.0, 0.6),
            ]
            for s_slug, req_prof, imp in aiml_reqs:
                s_obj = skills_by_slug.get(s_slug)
                if s_obj:
                    exists = db.execute(
                        select(RoleSkill).where(
                            RoleSkill.role_id == aiml_role.id,
                            RoleSkill.skill_id == s_obj.id
                        )
                    ).scalar_one_or_none()
                    if not exists:
                        rs = RoleSkill(
                            role_id=aiml_role.id,
                            skill_id=s_obj.id,
                            required_proficiency=req_prof,
                            importance=imp
                        )
                        db.add(rs)

        # ----------------------------------------------------------------------
        # 5. RESOURCES & RESOURCE-SKILL MAPPINGS
        # ----------------------------------------------------------------------
        resources_data = [
            {
                "title": "Python Programming Foundations",
                "description": "Comprehensive introduction to Python 3 for engineers, data analysis and algorithms.",
                "resource_type": "course",
                "provider": "PathFinder Academy",
                "url": "https://docs.python.org/3/tutorial/",
                "difficulty": "beginner",
                "estimated_minutes": 360,
                "quality_score": 92.0,
                "skills": [("python", 1.0), ("programming-fundamentals", 0.8)]
            },
            {
                "title": "Essential SQL for Data Workflows",
                "description": "Master SQL queries, table joins, window functions and analytical data transformations.",
                "resource_type": "tutorial",
                "provider": "PostgreSQL Official",
                "url": "https://www.postgresql.org/docs/current/tutorial.html",
                "difficulty": "beginner",
                "estimated_minutes": 240,
                "quality_score": 90.0,
                "skills": [("sql", 1.0)]
            },
            {
                "title": "Probability & Statistics for Machine Learning",
                "description": "Core statistical inference, probability distributions, variance, and hypothesis testing.",
                "resource_type": "course",
                "provider": "MIT OpenCourseWare",
                "url": "https://ocw.mit.edu/courses/mathematics/18-05-introduction-to-probability-and-statistics-spring-2014/",
                "difficulty": "intermediate",
                "estimated_minutes": 480,
                "quality_score": 95.0,
                "skills": [("statistics", 1.0), ("probability", 0.9)]
            },
            {
                "title": "Data Manipulation & Cleaning with Pandas & NumPy",
                "description": "High-performance data cleaning, vectorization, time series, and feature preparation.",
                "resource_type": "tutorial",
                "provider": "PyData",
                "url": "https://pandas.pydata.org/docs/getting_started/index.html",
                "difficulty": "intermediate",
                "estimated_minutes": 300,
                "quality_score": 91.0,
                "skills": [("data-processing", 1.0), ("python", 0.6)]
            },
            {
                "title": "Applied Machine Learning with Scikit-Learn",
                "description": "Supervised, unsupervised, regression, classification, decision trees, and ensemble methods.",
                "resource_type": "course",
                "provider": "Scikit-Learn Academy",
                "url": "https://scikit-learn.org/stable/tutorial/index.html",
                "difficulty": "intermediate",
                "estimated_minutes": 600,
                "quality_score": 96.0,
                "skills": [("machine-learning", 1.0), ("data-processing", 0.5)]
            },
            {
                "title": "Model Evaluation, Validation & Hyperparameter Tuning",
                "description": "Confusion matrix analysis, ROC-AUC, cross-validation strategies, avoiding leakage and overfitting.",
                "resource_type": "documentation",
                "provider": "ML Institute",
                "url": "https://scikit-learn.org/stable/modules/model_evaluation.html",
                "difficulty": "intermediate",
                "estimated_minutes": 240,
                "quality_score": 94.0,
                "skills": [("model-evaluation", 1.0), ("machine-learning", 0.6)]
            },
            {
                "title": "Model Evaluation Refresher & Diagnostic Guide",
                "description": "Targeted remediation module focusing on diagnostic errors, metric selection, and validation curves.",
                "resource_type": "tutorial",
                "provider": "PathFinder Labs",
                "url": "https://pathfinder.internal/resources/model-eval-refresher",
                "difficulty": "intermediate",
                "estimated_minutes": 180,
                "quality_score": 93.0,
                "skills": [("model-evaluation", 1.0)]
            },
            {
                "title": "Practical Feature Engineering for Tabular Data",
                "description": "Techniques for target encoding, handling outliers, binning, interaction features and PCA.",
                "resource_type": "tutorial",
                "provider": "Kaggle Learn",
                "url": "https://www.kaggle.com/learn/feature-engineering",
                "difficulty": "intermediate",
                "estimated_minutes": 200,
                "quality_score": 89.0,
                "skills": [("feature-engineering", 1.0), ("data-processing", 0.5)]
            },
            {
                "title": "Deep Learning Fundamentals with PyTorch",
                "description": "Tensors, autograd, feedforward networks, convolutional architectures, and loss optimization.",
                "resource_type": "course",
                "provider": "PyTorch Official",
                "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
                "difficulty": "advanced",
                "estimated_minutes": 540,
                "quality_score": 95.0,
                "skills": [("deep-learning", 1.0), ("python", 0.5)]
            },
            {
                "title": "Natural Language Processing with Transformers",
                "description": "Self-attention, BERT, GPT architectures, Hugging Face transformers, and text classification.",
                "resource_type": "tutorial",
                "provider": "Hugging Face",
                "url": "https://huggingface.co/learn/nlp-course/",
                "difficulty": "advanced",
                "estimated_minutes": 420,
                "quality_score": 94.0,
                "skills": [("nlp", 1.0), ("deep-learning", 0.6)]
            },
            {
                "title": "Computer Vision & Visual Feature Extraction",
                "description": "Image convolutions, ResNet architectures, transfer learning, and object detection with torchvision.",
                "resource_type": "tutorial",
                "provider": "PyTorch Vision",
                "url": "https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html",
                "difficulty": "advanced",
                "estimated_minutes": 360,
                "quality_score": 90.0,
                "skills": [("computer-vision", 1.0), ("deep-learning", 0.6)]
            },
            {
                "title": "Generative AI, LLMs & Retrieval-Augmented Generation (RAG)",
                "description": "Architecting vector-based knowledge retrieval, prompt optimization, LangChain/LangGraph pipelines.",
                "resource_type": "course",
                "provider": "DeepLearning.AI",
                "url": "https://www.deeplearning.ai/short-courses/",
                "difficulty": "advanced",
                "estimated_minutes": 480,
                "quality_score": 96.0,
                "skills": [("generative-ai", 1.0), ("nlp", 0.5)]
            },
            {
                "title": "Production MLOps, CI/CD & Model Monitoring",
                "description": "Packaging models, containerized deployment, drift detection, and automated retraining pipelines.",
                "resource_type": "course",
                "provider": "MLOps Community",
                "url": "https://ml-ops.org/",
                "difficulty": "advanced",
                "estimated_minutes": 400,
                "quality_score": 92.0,
                "skills": [("mlops", 1.0), ("docker", 0.6), ("apis", 0.5)]
            },
            {
                "title": "Git & GitHub Collaboration Workflow",
                "description": "Version control best practices, atomic commits, branch protection, and collaborative review.",
                "resource_type": "documentation",
                "provider": "GitHub",
                "url": "https://docs.github.com/en/get-started",
                "difficulty": "beginner",
                "estimated_minutes": 150,
                "quality_score": 91.0,
                "skills": [("git", 1.0)]
            },
            {
                "title": "FastAPI REST API Engineering",
                "description": "Building high-performance async REST services with Pydantic validation and automatic docs.",
                "resource_type": "tutorial",
                "provider": "FastAPI Official",
                "url": "https://fastapi.tiangolo.com/tutorial/",
                "difficulty": "intermediate",
                "estimated_minutes": 240,
                "quality_score": 95.0,
                "skills": [("apis", 1.0), ("python", 0.6)]
            },
            {
                "title": "Docker Containers for Developers",
                "description": "Container creation, image optimization, multi-stage builds, and docker-compose orchestration.",
                "resource_type": "course",
                "provider": "Docker Documentation",
                "url": "https://docs.docker.com/get-started/",
                "difficulty": "intermediate",
                "estimated_minutes": 220,
                "quality_score": 92.0,
                "skills": [("docker", 1.0)]
            },
            {
                "title": "Scalable ML System Design Patterns",
                "description": "Designing high-throughput ML architectures, feature stores, caching, and serving tradeoffs.",
                "resource_type": "course",
                "provider": "System Design Handbook",
                "url": "https://github.com/donnemartin/system-design-primer",
                "difficulty": "advanced",
                "estimated_minutes": 380,
                "quality_score": 93.0,
                "skills": [("system-design", 1.0), ("apis", 0.5)]
            }
        ]

        for res_info in resources_data:
            resource = db.execute(select(Resource).where(Resource.title == res_info["title"])).scalar_one_or_none()
            if not resource:
                resource = Resource(
                    title=res_info["title"],
                    description=res_info["description"],
                    resource_type=res_info["resource_type"],
                    provider=res_info["provider"],
                    url=res_info["url"],
                    difficulty=res_info["difficulty"],
                    estimated_minutes=res_info["estimated_minutes"],
                    quality_score=res_info["quality_score"],
                    is_active=True
                )
                db.add(resource)
                db.flush()
                print(f"Created Resource: {resource.title}")

            for s_slug, weight in res_info["skills"]:
                s_obj = skills_by_slug.get(s_slug)
                if s_obj:
                    exists = db.execute(
                        select(ResourceSkill).where(
                            ResourceSkill.resource_id == resource.id,
                            ResourceSkill.skill_id == s_obj.id
                        )
                    ).scalar_one_or_none()
                    if not exists:
                        rs = ResourceSkill(
                            resource_id=resource.id,
                            skill_id=s_obj.id,
                            coverage_weight=weight
                        )
                        db.add(rs)

        # ----------------------------------------------------------------------
        # 6. PROJECTS & PROJECT-SKILL MAPPINGS
        # ----------------------------------------------------------------------
        projects_data = [
            {
                "title": "Customer Churn Prediction & Model Evaluation",
                "description": "Build an end-to-end churn prediction model, perform feature engineering, and evaluate performance using ROC-AUC, PR curves and cross-validation.",
                "difficulty": "intermediate",
                "estimated_hours": 12.0,
                "instructions": "1. Ingest dataset\n2. Perform EDA & cleaning\n3. Engineer interaction features\n4. Train baseline vs tuned XGBoost\n5. Generate diagnostic confusion matrix & evaluation report.",
                "skills": [("machine-learning", 1.0), ("model-evaluation", 1.0), ("feature-engineering", 0.8), ("data-processing", 0.7)]
            },
            {
                "title": "Model Comparison & Diagnostic Evaluation Suite",
                "description": "Adaptive reinforcement project: Implement cross-validation benchmarking comparing Logistic Regression, Random Forest, and LightGBM with statistical hypothesis testing.",
                "difficulty": "intermediate",
                "estimated_hours": 8.0,
                "instructions": "1. Load classification benchmark\n2. Implement 5-fold Stratified CV\n3. Calculate F1, Precision, Recall and Brier score\n4. Document error patterns.",
                "skills": [("model-evaluation", 1.0), ("machine-learning", 0.8), ("statistics", 0.7)]
            },
            {
                "title": "RAG-Powered Domain Knowledge Assistant",
                "description": "Build a production-ready conversational search engine over unstructured documentation using embeddings, pgvector, and FastAPI.",
                "difficulty": "advanced",
                "estimated_hours": 16.0,
                "instructions": "1. Chunk documents\n2. Generate embeddings\n3. Store in pgvector\n4. Build FastAPI chat endpoint\n5. Implement grounded citation prompt.",
                "skills": [("generative-ai", 1.0), ("nlp", 0.8), ("apis", 0.8), ("python", 0.7)]
            },
            {
                "title": "End-to-End MLOps Serving Pipeline",
                "description": "Containerize a trained model in FastAPI, package in Docker, and configure automated GitHub Actions CI/CD tests.",
                "difficulty": "advanced",
                "estimated_hours": 14.0,
                "instructions": "1. Export serialized ONNX/sklearn model\n2. Build FastAPI inference server\n3. Containerize via Docker multi-stage build\n4. Write pytest test suite.",
                "skills": [("mlops", 1.0), ("docker", 0.9), ("apis", 0.8), ("git", 0.7)]
            }
        ]

        for p_info in projects_data:
            project = db.execute(select(Project).where(Project.title == p_info["title"])).scalar_one_or_none()
            if not project:
                project = Project(
                    title=p_info["title"],
                    description=p_info["description"],
                    difficulty=p_info["difficulty"],
                    estimated_hours=p_info["estimated_hours"],
                    instructions=p_info["instructions"]
                )
                db.add(project)
                db.flush()
                print(f"Created Project: {project.title}")

            for s_slug, weight in p_info["skills"]:
                s_obj = skills_by_slug.get(s_slug)
                if s_obj:
                    exists = db.execute(
                        select(ProjectSkill).where(
                            ProjectSkill.project_id == project.id,
                            ProjectSkill.skill_id == s_obj.id
                        )
                    ).scalar_one_or_none()
                    if not exists:
                        ps = ProjectSkill(
                            project_id=project.id,
                            skill_id=s_obj.id,
                            coverage_weight=weight
                        )
                        db.add(ps)

        # ----------------------------------------------------------------------
        # 7. ASSESSMENTS & ASSESSMENT QUESTIONS
        # ----------------------------------------------------------------------
        assessments_data = [
            {
                "skill_slug": "python",
                "title": "Python Foundations & Data Structures",
                "description": "Evaluate knowledge of core Python syntax, collections, list comprehensions, and generators.",
                "difficulty": "beginner",
                "passing_score": 70.0,
                "questions": [
                    {
                        "question": "What is the time complexity of looking up a key in a standard Python dictionary (average case)?",
                        "question_type": "multiple_choice",
                        "options": {"A": "O(n)", "B": "O(log n)", "C": "O(1)", "D": "O(n log n)"},
                        "correct_answer": "C",
                        "explanation": "Python dictionaries are implemented as hash tables, providing O(1) average lookup time.",
                        "points": 1.0
                    },
                    {
                        "question": "Which Python built-in is used to iterate over both indices and elements of a sequence?",
                        "question_type": "multiple_choice",
                        "options": {"A": "zip()", "B": "enumerate()", "C": "range()", "D": "map()"},
                        "correct_answer": "B",
                        "explanation": "enumerate() returns pairs of (index, element) during iteration.",
                        "points": 1.0
                    }
                ]
            },
            {
                "skill_slug": "statistics",
                "title": "Statistical Foundations & Hypothesis Testing",
                "description": "Assess understanding of probability distributions, p-values, central limit theorem, and variance.",
                "difficulty": "intermediate",
                "passing_score": 70.0,
                "questions": [
                    {
                        "question": "What does a p-value less than alpha (e.g. 0.05) indicate in statistical hypothesis testing?",
                        "question_type": "multiple_choice",
                        "options": {
                            "A": "The null hypothesis is definitively true.",
                            "B": "The sample size is too small.",
                            "C": "There is sufficient evidence to reject the null hypothesis.",
                            "D": "The alternative hypothesis has a 95% probability of being true."
                        },
                        "correct_answer": "C",
                        "explanation": "A p-value below alpha indicates that observed results are unlikely under the null hypothesis, allowing rejection.",
                        "points": 1.0
                    },
                    {
                        "question": "According to the Central Limit Theorem, the distribution of sample means approaches what distribution as sample size grows?",
                        "question_type": "multiple_choice",
                        "options": {"A": "Uniform", "B": "Normal", "C": "Exponential", "D": "Binomial"},
                        "correct_answer": "B",
                        "explanation": "The CLT states that sample means approximate a normal distribution for sufficiently large N.",
                        "points": 1.0
                    }
                ]
            },
            {
                "skill_slug": "machine-learning",
                "title": "Machine Learning Core Concepts",
                "description": "Assess grasp of bias-variance tradeoff, regularization, and model algorithms.",
                "difficulty": "intermediate",
                "passing_score": 70.0,
                "questions": [
                    {
                        "question": "What is the primary purpose of L2 Regularization (Ridge) in linear models?",
                        "question_type": "multiple_choice",
                        "options": {
                            "A": "Set uninformative feature coefficients exactly to zero.",
                            "B": "Penalize large weights to reduce overfitting.",
                            "C": "Accelerate stochastic gradient descent convergence.",
                            "D": "Eliminate the need for validation splits."
                        },
                        "correct_answer": "B",
                        "explanation": "L2 regularization shrinks weights towards zero via squared magnitude penalty, reducing variance and overfitting.",
                        "points": 1.0
                    },
                    {
                        "question": "Which algorithm constructs an ensemble of decision trees sequentially to correct predecessor errors?",
                        "question_type": "multiple_choice",
                        "options": {"A": "Random Forest", "B": "K-Means", "C": "Gradient Boosted Trees", "D": "Support Vector Machine"},
                        "correct_answer": "C",
                        "explanation": "Boosting trains models sequentially where each new tree fits the residual errors of the prior ensemble.",
                        "points": 1.0
                    }
                ]
            },
            {
                "skill_slug": "model-evaluation",
                "title": "Model Evaluation & Validation Assessment",
                "description": "Assess precision, recall, ROC-AUC, cross-validation, and diagnostic metric selection.",
                "difficulty": "intermediate",
                "passing_score": 75.0,
                "questions": [
                    {
                        "question": "In a highly imbalanced fraud detection dataset (0.1% positive class), which metric is LEAST informative for model quality?",
                        "question_type": "multiple_choice",
                        "options": {"A": "Raw Accuracy", "B": "Precision-Recall AUC", "C": "F1-Score", "D": "Recall at 99% Precision"},
                        "correct_answer": "A",
                        "explanation": "A model predicting always-negative achieves 99.9% accuracy on a 0.1% positive dataset while detecting 0 fraud cases.",
                        "points": 1.0
                    },
                    {
                        "question": "What cross-validation strategy should be used to maintain class proportion in each fold for classification?",
                        "question_type": "multiple_choice",
                        "options": {"A": "Leave-One-Out CV", "B": "Stratified K-Fold CV", "C": "Shuffle Split without stratification", "D": "Time Series Split"},
                        "correct_answer": "B",
                        "explanation": "Stratified K-Fold ensures each fold has approximately the same percentage of samples of each target class.",
                        "points": 1.0
                    },
                    {
                        "question": "High training accuracy paired with substantially lower validation accuracy is a classic symptom of:",
                        "question_type": "multiple_choice",
                        "options": {"A": "High bias (underfitting)", "B": "High variance (overfitting)", "C": "Data leakage in test set", "D": "Optimal convergence"},
                        "correct_answer": "B",
                        "explanation": "A large gap between training and validation accuracy indicates the model has memorized training noise (overfitting).",
                        "points": 1.0
                    }
                ]
            },
            {
                "skill_slug": "generative-ai",
                "title": "Generative AI & RAG Architecture Assessment",
                "description": "Assess understanding of embeddings, vector similarity search, chunking, and hallucination reduction.",
                "difficulty": "advanced",
                "passing_score": 70.0,
                "questions": [
                    {
                        "question": "In a Retrieval-Augmented Generation (RAG) system, what is the primary role of vector similarity search?",
                        "question_type": "multiple_choice",
                        "options": {
                            "A": "Directly generate natural language tokens.",
                            "B": "Retrieve the most semantically relevant document chunks to inject as context into the prompt.",
                            "C": "Validate the syntax of Python API calls.",
                            "D": "Fine-tune model weights on the user query."
                        },
                        "correct_answer": "B",
                        "explanation": "Vector retrieval identifies nearest neighbor chunks in embedding space to ground the LLM's generation.",
                        "points": 1.0
                    },
                    {
                        "question": "Why should raw user input never be trusted to directly construct system instructions or database queries?",
                        "question_type": "multiple_choice",
                        "options": {
                            "A": "It increases token costs unnecessarily.",
                            "B": "It exposes the application to prompt injection and SQL injection attacks.",
                            "C": "Vector embeddings cannot parse user text.",
                            "D": "FastAPI does not allow strings in request bodies."
                        },
                        "correct_answer": "B",
                        "explanation": "Untrusted input requires strict schema validation and sanitization to prevent prompt injection and unauthorized access.",
                        "points": 1.0
                    }
                ]
            }
        ]

        for a_info in assessments_data:
            s_obj = skills_by_slug.get(a_info["skill_slug"])
            if s_obj:
                assessment = db.execute(select(Assessment).where(Assessment.title == a_info["title"])).scalar_one_or_none()
                if not assessment:
                    assessment = Assessment(
                        skill_id=s_obj.id,
                        title=a_info["title"],
                        description=a_info["description"],
                        difficulty=a_info["difficulty"],
                        passing_score=a_info["passing_score"]
                    )
                    db.add(assessment)
                    db.flush()
                    print(f"Created Assessment: {assessment.title}")

                for q_info in a_info["questions"]:
                    exists = db.execute(
                        select(AssessmentQuestion).where(
                            AssessmentQuestion.assessment_id == assessment.id,
                            AssessmentQuestion.question == q_info["question"]
                        )
                    ).scalar_one_or_none()
                    if not exists:
                        q = AssessmentQuestion(
                            assessment_id=assessment.id,
                            question=q_info["question"],
                            question_type=q_info["question_type"],
                            options=q_info["options"],
                            correct_answer=q_info["correct_answer"],
                            explanation=q_info["explanation"],
                            points=q_info["points"]
                        )
                        db.add(q)

        # ----------------------------------------------------------------------
        # 10. DEMO USERS & PROFILES (Phase 17)
        # ----------------------------------------------------------------------
        demo_users_data = [
            {
                "name": "Alex Chen (Demo AI Engineer)",
                "email": "demo@pathfinder.ai",
                "password": "Password@123",
                "target_role_slug": "ai-ml-engineer",
                "experience_level": "intermediate",
                "daily_study_hours": 2.5,
                "target_duration_weeks": 12,
                "skills": [
                    {"skill_slug": "python", "proficiency": 75},
                    {"skill_slug": "programming-fundamentals", "proficiency": 85},
                    {"skill_slug": "statistics", "proficiency": 60},
                    {"skill_slug": "sql", "proficiency": 70},
                ]
            },
            {
                "name": "Priya Sharma (Data Scientist)",
                "email": "priya@pathfinder.ai",
                "password": "Password@123",
                "target_role_slug": "data-scientist",
                "experience_level": "beginner",
                "daily_study_hours": 2.0,
                "target_duration_weeks": 16,
                "skills": [
                    {"skill_slug": "python", "proficiency": 40},
                    {"skill_slug": "statistics", "proficiency": 50},
                ]
            },
            {
                "name": "Sam Taylor (Full Stack)",
                "email": "sam@pathfinder.ai",
                "password": "Password@123",
                "target_role_slug": "full-stack-developer",
                "experience_level": "intermediate",
                "daily_study_hours": 3.0,
                "target_duration_weeks": 10,
                "skills": [
                    {"skill_slug": "programming-fundamentals", "proficiency": 90},
                    {"skill_slug": "sql", "proficiency": 80},
                ]
            }
        ]

        for u_info in demo_users_data:
            existing_u = db.execute(select(User).where(User.email == u_info["email"])).scalar_one_or_none()
            if not existing_u:
                target_role = roles_by_slug.get(u_info["target_role_slug"])
                new_u = User(
                    name=u_info["name"],
                    email=u_info["email"],
                    password_hash=hash_password(u_info["password"]),
                    is_active=True
                )
                db.add(new_u)
                db.flush()

                new_prof = LearnerProfile(
                    user_id=new_u.id,
                    target_role_id=target_role.id if target_role else None,
                    experience_level=u_info["experience_level"],
                    daily_study_hours=u_info["daily_study_hours"],
                    target_duration_weeks=u_info["target_duration_weeks"],
                    learning_preferences={"style": "hands-on", "pace": "moderate", "notifications": True}
                )
                db.add(new_prof)
                db.flush()

                for s_item in u_info["skills"]:
                    s_obj = skills_by_slug.get(s_item["skill_slug"])
                    if s_obj:
                        l_skill = LearnerSkill(
                            learner_id=new_prof.id,
                            skill_id=s_obj.id,
                            proficiency=s_item["proficiency"],
                            source="self_assessment"
                        )
                        db.add(l_skill)
                print(f"Created Demo User: {new_u.email} (Password: {u_info['password']})")

        db.commit()

        # ----------------------------------------------------------------------
        # 11. PRE-GENERATE DEMO ROADMAPS & TELEMETRY
        # ----------------------------------------------------------------------
        from backend.app.services.roadmap_service import RoadmapService
        from backend.app.repositories.roadmap_repository import RoadmapRepository
        from backend.app.models.roadmap import Roadmap

        for u_info in demo_users_data:
            demo_u = db.execute(select(User).where(User.email == u_info["email"])).scalar_one_or_none()
            if demo_u and demo_u.profile and demo_u.profile.target_role_id:
                has_rm = db.execute(select(Roadmap).where(Roadmap.learner_id == demo_u.profile.id)).scalar_one_or_none()
                if not has_rm:
                    try:
                        rm_resp = RoadmapService.generate_roadmap(db, demo_u.id)
                        print(f"Generated Roadmap for {demo_u.email}")
                    except Exception as ex:
                        print(f"Note: Roadmap generation for {demo_u.email}: {ex}")

                # Ensure demo progress for demo@pathfinder.ai
                if demo_u.email == "demo@pathfinder.ai":
                    active_rm = RoadmapRepository.get_active_roadmap(db, demo_u.profile.id)
                    if active_rm and active_rm.items:
                        sorted_items = sorted(active_rm.items, key=lambda it: it.sequence)
                        first_it = sorted_items[0]
                        if first_it.status != "COMPLETED":
                            RoadmapService.start_roadmap_item(db, demo_u.id, first_it.id)
                            RoadmapService.complete_roadmap_item(db, demo_u.id, first_it.id)
                            if len(sorted_items) > 1:
                                second_it = sorted_items[1]
                                if second_it.status != "IN_PROGRESS":
                                    RoadmapService.start_roadmap_item(db, demo_u.id, second_it.id)
                            print(f"Advanced milestone progress for {demo_u.email}")

        db.commit()
        print("--- PathFinder AI Seed Process Completed Successfully! ---")
        return True
    except Exception as e:
        db.rollback()
        print(f"ERROR during seed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
