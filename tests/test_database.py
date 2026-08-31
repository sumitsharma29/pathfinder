import uuid
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from backend.app.models import (
    User, LearnerProfile, Skill, Role, RoleSkill,
    LearnerSkill, SkillPrerequisite, Resource, ResourceSkill,
    Project, ProjectSkill, Assessment, AssessmentQuestion,
    AssessmentResult, Roadmap, RoadmapItem, Recommendation,
    Feedback, Progress, Conversation, ConversationMessage,
    RoadmapVersion
)


def test_user_creation(db_session):
    """Test 1: User creation with valid attributes."""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Test Learner",
        email=unique_email,
        password_hash="argon2_hashed_secret_password_123",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    queried = db_session.execute(select(User).where(User.id == user.id)).scalar_one_or_none()
    assert queried is not None
    assert queried.email == unique_email
    assert queried.is_active is True
    assert queried.id is not None
    assert queried.created_at is not None


def test_learner_profile_ownership(db_session):
    """Test 2: Learner profile ownership and 1-to-1 link with User."""
    unique_email = f"profile_owner_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Profile Owner",
        email=unique_email,
        password_hash="hashed_secret"
    )
    db_session.add(user)
    db_session.flush()

    profile = LearnerProfile(
        user_id=user.id,
        experience_level="beginner",
        daily_study_hours=2.5,
        target_duration_weeks=12,
        learning_preferences={"style": "hands-on", "pace": "moderate"}
    )
    db_session.add(profile)
    db_session.commit()

    assert user.profile is not None
    assert user.profile.id == profile.id
    assert user.profile.daily_study_hours == 2.5


def test_unique_email_constraint(db_session):
    """Test 3: Unique email constraint rejection."""
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    user1 = User(name="User 1", email=email, password_hash="hash1")
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("INSERT INTO users (id, name, email, password_hash, is_active) VALUES (gen_random_uuid(), 'User 2', :email, 'hash2', true)"),
            {"email": email}
        )
        db_session.commit()
    db_session.rollback()


def test_unique_skill_slug(db_session):
    """Test 4: Unique skill slug constraint."""
    slug = f"skill-{uuid.uuid4().hex[:8]}"
    skill1 = Skill(name=f"Skill 1 {slug}", slug=slug, category="General")
    db_session.add(skill1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("INSERT INTO skills (id, name, slug, category) VALUES (gen_random_uuid(), :name, :slug, 'General')"),
            {"name": f"Skill 2 {slug}", "slug": slug}
        )
        db_session.commit()
    db_session.rollback()


def test_role_skill_composite_uniqueness(db_session):
    """Test 5: Composite PK uniqueness on role_skills."""
    role = Role(name=f"Role {uuid.uuid4().hex[:6]}", slug=f"role-{uuid.uuid4().hex[:6]}")
    skill = Skill(name=f"Skill {uuid.uuid4().hex[:6]}", slug=f"skill-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add_all([role, skill])
    db_session.commit()

    rs1 = RoleSkill(role_id=role.id, skill_id=skill.id, required_proficiency=80.0, importance=0.9)
    db_session.add(rs1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("INSERT INTO role_skills (role_id, skill_id, required_proficiency, importance) VALUES (:role_id, :skill_id, 90.0, 1.0)"),
            {"role_id": str(role.id), "skill_id": str(skill.id)}
        )
        db_session.commit()
    db_session.rollback()


def test_learner_skill_composite_uniqueness(db_session):
    """Test 6: Composite PK uniqueness on learner_skills."""
    user = User(name="Skill User", email=f"user_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    profile = LearnerProfile(user_id=user.id)
    skill = Skill(name=f"Skill {uuid.uuid4().hex[:6]}", slug=f"skill-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add_all([profile, skill])
    db_session.commit()

    ls1 = LearnerSkill(learner_id=profile.id, skill_id=skill.id, proficiency=60.0, source="self_declared")
    db_session.add(ls1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("INSERT INTO learner_skills (learner_id, skill_id, proficiency, source) VALUES (:learner_id, :skill_id, 75.0, 'assessment')"),
            {"learner_id": str(profile.id), "skill_id": str(skill.id)}
        )
        db_session.commit()
    db_session.rollback()


def test_prerequisite_self_reference_rejection(db_session):
    """Test 7: Self-referential prerequisite check constraint violation."""
    skill = Skill(name=f"Self Skill {uuid.uuid4().hex[:6]}", slug=f"self-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add(skill)
    db_session.flush()

    self_prereq = SkillPrerequisite(skill_id=skill.id, prerequisite_skill_id=skill.id, strength=1.0)
    db_session.add(self_prereq)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_proficiency_constraints(db_session):
    """Test 8: Proficiency CHECK constraint boundaries (0-100)."""
    user = User(name="Prof User", email=f"prof_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    profile = LearnerProfile(user_id=user.id)
    skill = Skill(name=f"Skill {uuid.uuid4().hex[:6]}", slug=f"skill-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add_all([profile, skill])
    db_session.flush()

    invalid_ls = LearnerSkill(learner_id=profile.id, skill_id=skill.id, proficiency=120.0, source="self_declared")
    db_session.add(invalid_ls)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_resource_quality_constraints(db_session):
    """Test 9: Resource quality score CHECK constraint (0-100)."""
    invalid_res = Resource(
        title="Invalid Resource",
        resource_type="course",
        url="https://example.com",
        quality_score=150.0
    )
    db_session.add(invalid_res)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_assessment_score_constraints(db_session):
    """Test 10: Assessment passing score CHECK constraint (0-100)."""
    skill = Skill(name=f"Skill {uuid.uuid4().hex[:6]}", slug=f"skill-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add(skill)
    db_session.flush()

    invalid_assessment = Assessment(
        skill_id=skill.id,
        title="Invalid Assessment",
        passing_score=110.0
    )
    db_session.add(invalid_assessment)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_roadmap_sequence_uniqueness(db_session):
    """Test 11: Roadmap items sequence uniqueness per roadmap."""
    user = User(name="Roadmap User", email=f"rm_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    profile = LearnerProfile(user_id=user.id)
    role = Role(name=f"Role {uuid.uuid4().hex[:6]}", slug=f"role-{uuid.uuid4().hex[:6]}")
    db_session.add_all([profile, role])
    db_session.flush()

    roadmap = Roadmap(learner_id=profile.id, target_role_id=role.id, version=1)
    db_session.add(roadmap)
    db_session.flush()

    item1 = RoadmapItem(roadmap_id=roadmap.id, sequence=1, status="AVAILABLE", progress=0.0)
    item2 = RoadmapItem(roadmap_id=roadmap.id, sequence=1, status="LOCKED", progress=0.0)
    db_session.add(item1)
    db_session.commit()

    db_session.add(item2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_assessment_attempt_uniqueness(db_session):
    """Test 12: Assessment result attempt uniqueness per learner & assessment."""
    user = User(name="Result User", email=f"res_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    profile = LearnerProfile(user_id=user.id)
    skill = Skill(name=f"Skill {uuid.uuid4().hex[:6]}", slug=f"skill-{uuid.uuid4().hex[:6]}", category="General")
    db_session.add_all([profile, skill])
    db_session.flush()

    assessment = Assessment(skill_id=skill.id, title="Test Exam", passing_score=70.0)
    db_session.add(assessment)
    db_session.flush()

    res1 = AssessmentResult(assessment_id=assessment.id, learner_id=profile.id, score=85.0, skill_mastery=85.0, attempt_number=1)
    res2 = AssessmentResult(assessment_id=assessment.id, learner_id=profile.id, score=90.0, skill_mastery=90.0, attempt_number=1)
    db_session.add(res1)
    db_session.commit()

    db_session.add(res2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_delete_behavior(db_session):
    """Test 13: Cascade deletion of tightly-coupled children (messages with conversation)."""
    user = User(name="Conv User", email=f"conv_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    profile = LearnerProfile(user_id=user.id)
    db_session.add(profile)
    db_session.flush()

    conv = Conversation(learner_id=profile.id, title="Test Chat")
    db_session.add(conv)
    db_session.flush()

    msg = ConversationMessage(conversation_id=conv.id, role="user", content="Hello PathFinder")
    db_session.add(msg)
    db_session.commit()

    conv_id = conv.id
    msg_id = msg.id

    # Delete conversation -> should cascade delete message
    db_session.delete(conv)
    db_session.commit()

    deleted_msg = db_session.execute(select(ConversationMessage).where(ConversationMessage.id == msg_id)).scalar_one_or_none()
    assert deleted_msg is None


def test_restricted_delete_behavior(db_session):
    """Test 14: RESTRICT deletion prevents deleting referenced canonical roles/skills."""
    user = User(name="Restricted User", email=f"restr_{uuid.uuid4().hex[:8]}@example.com", password_hash="h")
    role = Role(name=f"Restricted Role {uuid.uuid4().hex[:6]}", slug=f"restr-{uuid.uuid4().hex[:6]}")
    db_session.add_all([user, role])
    db_session.flush()

    profile = LearnerProfile(user_id=user.id, target_role_id=role.id)
    db_session.add(profile)
    db_session.commit()

    # Attempting to delete role in database while referenced by learner_profile must raise IntegrityError (RESTRICT)
    with pytest.raises(IntegrityError):
        db_session.execute(text("DELETE FROM roles WHERE id = :role_id"), {"role_id": str(role.id)})
        db_session.commit()
    db_session.rollback()


def test_vector_column_support(db_session):
    """Test 15: Vector column functionality on resources."""
    res = Resource(
        title=f"Vector Resource {uuid.uuid4().hex[:6]}",
        resource_type="course",
        url="https://example.com/vector",
        embedding=[0.1, 0.2, 0.3, 0.4]
    )
    db_session.add(res)
    db_session.commit()

    queried = db_session.execute(select(Resource).where(Resource.id == res.id)).scalar_one_or_none()
    assert queried is not None
    assert queried.embedding is not None
    assert len(queried.embedding) == 4
    assert abs(queried.embedding[0] - 0.1) < 1e-4
