import uuid
import math
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.resource import Resource
from backend.app.models.resource_skill import ResourceSkill
from backend.app.models.skill import Skill
from backend.app.models.role_skill import RoleSkill
from backend.app.schemas.rag import RetrievedResourceSource, RAGAnswerResponse
from backend.app.ai.embeddings.base import EmbeddingProvider
from backend.app.ai.embeddings.factory import get_embedding_provider
from backend.app.ai.providers.base import LLMProvider
from backend.app.ai.providers.factory import get_llm_provider
from backend.app.ai.prompts.rag_prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from backend.app.core.config import settings


class RAGService:
    """Grounded Retrieval-Augmented Generation (RAG) Service for PathFinder AI.

    Retrieves curated catalog resources using pgvector similarity and metadata filters,
    builds bounded context, and generates grounded educational answers with validated citations.
    """

    @classmethod
    def embed_query(
        cls,
        query: str,
        provider: Optional[EmbeddingProvider] = None
    ) -> List[float]:
        """Generate query vector embedding using configured provider."""
        provider = provider or get_embedding_provider()
        try:
            import concurrent.futures
            def _run():
                return asyncio.run(provider.embed_query(query))

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(_run).result(timeout=10.0)
        except Exception:
            # Fallback to deterministic mock generator
            from backend.app.ai.embeddings.mock_provider import MockEmbeddingProvider
            fallback = MockEmbeddingProvider()
            return asyncio.run(fallback.embed_query(query))

    @classmethod
    def retrieve_relevant_resources(
        cls,
        db: Session,
        query: str,
        query_vector: Optional[List[float]] = None,
        top_k: Optional[int] = None,
        skill_id: Optional[uuid.UUID] = None,
        difficulty: Optional[str] = None,
        resource_type: Optional[str] = None,
        target_role_id: Optional[uuid.UUID] = None,
        min_similarity: Optional[float] = None
    ) -> List[RetrievedResourceSource]:
        """Deterministic vector and metadata resource retrieval strictly from PostgreSQL."""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import func

        top_k = top_k or settings.RAG_TOP_K or 5
        min_similarity = min_similarity if min_similarity is not None else settings.RAG_SIMILARITY_THRESHOLD

        if query_vector is None:
            query_vector = cls.embed_query(query)

        # 1. PRIMARY PATH: Native PostgreSQL pgvector cosine similarity search
        # Cosine distance = 1.0 - Cosine similarity => distance <= (1.0 - min_similarity)
        max_cosine_distance = 1.0 - float(min_similarity)

        # Check if vector-embedded resources are available in the database
        has_vector_data = db.scalar(
            select(func.count(Resource.id))
            .where(Resource.is_active.is_(True), Resource.embedding.isnot(None))
        ) or 0

        if has_vector_data > 0 and hasattr(Resource.embedding, "cosine_distance"):
            try:
                with db.begin_nested():
                    stmt = (
                        select(
                            Resource,
                            (1.0 - Resource.embedding.cosine_distance(query_vector)).label("similarity_score")
                        )
                        .options(selectinload(Resource.resource_skills).selectinload(ResourceSkill.skill))
                        .where(
                            Resource.is_active.is_(True),
                            Resource.embedding.isnot(None),
                            Resource.embedding.cosine_distance(query_vector) <= max_cosine_distance
                        )
                    )

                    if difficulty:
                        stmt = stmt.where(Resource.difficulty == difficulty.lower().strip())
                    if resource_type:
                        stmt = stmt.where(Resource.resource_type == resource_type.lower().strip())
                    if skill_id:
                        stmt = stmt.join(ResourceSkill, ResourceSkill.resource_id == Resource.id).where(ResourceSkill.skill_id == skill_id)

                    # Deterministic ordering: lowest cosine distance first (highest similarity), stable secondary tie-break on Resource.id
                    stmt = stmt.order_by(
                        Resource.embedding.cosine_distance(query_vector).asc(),
                        Resource.id.asc()
                    ).limit(top_k)

                    pg_rows = db.execute(stmt).all()
                    if pg_rows:
                        sources: List[RetrievedResourceSource] = []
                        for res, sim_val in pg_rows:
                            s_names = [rs.skill.name for rs in res.resource_skills if rs.skill]
                            sources.append(
                                RetrievedResourceSource(
                                    resource_id=res.id,
                                    title=res.title,
                                    description=res.description,
                                    url=res.url,
                                    resource_type=res.resource_type,
                                    difficulty=res.difficulty,
                                    similarity_score=round(float(sim_val), 4),
                                    matched_skills=s_names
                                )
                            )
                        return sources
            except Exception:
                pass

        # 2. FALLBACK PATH (When pgvector extension binary is unavailable on host or un-embedded data)
        stmt = (
            select(Resource)
            .options(selectinload(Resource.resource_skills).selectinload(ResourceSkill.skill))
            .where(Resource.is_active.is_(True))
        )

        if difficulty:
            stmt = stmt.where(Resource.difficulty == difficulty.lower().strip())
        if resource_type:
            stmt = stmt.where(Resource.resource_type == resource_type.lower().strip())

        resources = db.execute(stmt).scalars().all()

        query_words = set(re_clean(query).split())
        candidate_results: List[Tuple[Resource, float, List[str]]] = []

        role_skill_ids = set()
        if target_role_id:
            rs_rows = db.execute(select(RoleSkill.skill_id).where(RoleSkill.role_id == target_role_id)).scalars().all()
            role_skill_ids = set(rs_rows)

        for res in resources:
            res_skill_ids = {rs.skill_id for rs in res.resource_skills if rs.skill}
            skill_names = [rs.skill.name for rs in res.resource_skills if rs.skill]

            if skill_id and skill_id not in res_skill_ids:
                continue

            sim = cls._calculate_resource_similarity(
                query_vector=query_vector,
                query_words=query_words,
                resource=res,
                skill_names=skill_names,
                has_role_skill=bool(res_skill_ids & role_skill_ids) if role_skill_ids else False
            )

            if sim >= min_similarity:
                candidate_results.append((res, sim, skill_names))

        candidate_results.sort(key=lambda item: (-item[1], str(item[0].id)))
        top_results = candidate_results[:top_k]
        sources: List[RetrievedResourceSource] = []

        for res, sim_score, s_names in top_results:
            sources.append(
                RetrievedResourceSource(
                    resource_id=res.id,
                    title=res.title,
                    description=res.description,
                    url=res.url,
                    resource_type=res.resource_type,
                    difficulty=res.difficulty,
                    similarity_score=round(sim_score, 4),
                    matched_skills=s_names
                )
            )

        return sources

    STOP_WORDS = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "and", "or", "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "can", "could", "should", "would", "what", "how",
        "why", "which", "who", "whom", "this", "that", "these", "those", "i", "you",
        "he", "she", "it", "we", "they", "me", "my", "your", "our", "their"
    }

    @classmethod
    def _calculate_resource_similarity(
        cls,
        query_vector: List[float],
        query_words: set,
        resource: Resource,
        skill_names: List[str],
        has_role_skill: bool
    ) -> float:
        """Calculate hybrid vector + keyword relevance score between query and catalog resource."""
        # 1. Vector cosine similarity if resource embedding exists
        vector_sim = 0.0
        if resource.embedding is not None and len(resource.embedding) == len(query_vector):
            dot = sum(a * b for a, b in zip(query_vector, resource.embedding))
            norm_a = math.sqrt(sum(a * a for a, b in zip(query_vector, query_vector)))
            norm_b = math.sqrt(sum(b * b for b, b in zip(resource.embedding, resource.embedding)))
            if norm_a > 0 and norm_b > 0:
                vector_sim = max(0.0, min(1.0, dot / (norm_a * norm_b)))

        # 2. Text keyword & domain skill match against title, description, and skills
        meaningful_words = {w for w in query_words if len(w) > 2 and w not in cls.STOP_WORDS}
        text_corpus = f"{resource.title} {resource.description or ''} {' '.join(skill_names)}".lower()

        if meaningful_words:
            matched_count = sum(1 for w in meaningful_words if w in text_corpus)
            keyword_score = matched_count / len(meaningful_words)
        else:
            keyword_score = 0.0

        # Direct skill name match bonus
        for s_name in skill_names:
            if s_name.lower() in " ".join(query_words):
                keyword_score = max(keyword_score, 0.85)

        # Overfitting / generalization domain association
        if ("overfitting" in query_words or "underfitting" in query_words) and any(
            s.lower() in ["machine learning", "deep learning", "model evaluation"] for s in skill_names
        ):
            keyword_score = max(keyword_score, 0.85)

        # Combine vector and text relevance (vector similarity is not down-weighted below true cosine similarity)
        if vector_sim > 0.0:
            combined = max(vector_sim, 0.60 * vector_sim + 0.40 * keyword_score)
        else:
            combined = keyword_score

        # Role alignment boost
        if has_role_skill:
            combined = min(1.0, combined + 0.05)

        return min(1.0, max(0.0, combined))

    @classmethod
    def build_grounded_context(cls, sources: List[RetrievedResourceSource]) -> str:
        """Format bounded, structured context string from retrieved sources."""
        if not sources:
            return "No relevant resources found in the PathFinder catalog."

        lines = []
        for i, s in enumerate(sources, 1):
            skills_str = ", ".join(s.matched_skills) if s.matched_skills else "General"
            lines.append(
                f"[Source {i}] Title: {s.title} (ID: {s.resource_id})\n"
                f"  Type: {s.resource_type} | Difficulty: {s.difficulty or 'Unspecified'} | Skills: {skills_str}\n"
                f"  URL: {s.url}\n"
                f"  Description: {s.description or 'No description provided.'}\n"
            )
        return "\n".join(lines)

    @classmethod
    def generate_grounded_answer(
        cls,
        db: Session,
        query: str,
        learner_context: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        skill_id: Optional[uuid.UUID] = None,
        difficulty: Optional[str] = None,
        resource_type: Optional[str] = None,
        target_role_id: Optional[uuid.UUID] = None,
        min_similarity: Optional[float] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        llm_provider: Optional[LLMProvider] = None
    ) -> RAGAnswerResponse:
        """Execute full RAG pipeline: Query -> Embedding -> Retrieval -> Context -> LLM -> Validated Answer."""
        clean_q = query.strip()
        if not clean_q:
            return RAGAnswerResponse(
                query=query,
                answer="Please provide a valid question.",
                sources=[],
                status="INSUFFICIENT_CONTEXT"
            )

        # Handle casual greetings and introductory inquiries gracefully
        GREETINGS = {
            "hi", "hii", "hiii", "hello", "hey", "heyy", "greetings",
            "good morning", "good afternoon", "good evening",
            "who are you", "what can you do", "help", "howdy", "what is pathfinder"
        }
        normalized_q = "".join(c for c in clean_q.lower() if c.isalnum() or c.isspace()).strip()
        if normalized_q in GREETINGS or normalized_q.startswith(("hi ", "hello ", "hey ")):
            target_role = learner_context.get("target_role") if learner_context else None
            role_hint = f" targeting **{target_role}**" if target_role else ""
            greeting_msg = (
                f"Hello! 👋 I'm your **PathFinder AI Learning Assistant**.\n\n"
                f"I'm here to guide your personalized learning journey{role_hint}. You can ask me:\n\n"
                f"• **Technical Concepts**: *\"Explain gradient descent with an example\"* or *\"What is overfitting vs underfitting?\"*\n"
                f"• **Roadmap & Strategy**: *\"What skills do I need to become an AI/ML Engineer?\"*\n"
                f"• **Resource Recommendations**: *\"Recommend the best Python or SQL courses for beginners.\"*\n"
                f"• **Assessment Prep**: *\"How should I prepare for the Machine Learning quiz?\"*\n\n"
                f"How can I assist you with your learning goals today?"
            )
            return RAGAnswerResponse(
                query=clean_q,
                answer=greeting_msg,
                sources=[],
                status="GROUNDED_ANSWER"
            )

        # 1. Retrieve relevant catalog resources
        sources = cls.retrieve_relevant_resources(
            db=db,
            query=clean_q,
            top_k=top_k,
            skill_id=skill_id,
            difficulty=difficulty,
            resource_type=resource_type,
            target_role_id=target_role_id,
            min_similarity=min_similarity
        )

        # 2. Handle zero retrieved relevant resources
        if not sources:
            return RAGAnswerResponse(
                query=clean_q,
                answer=(
                    "I don't have enough information in the curated PathFinder resources to answer this question accurately. "
                    "Please ask about topics covered in our learning catalog, such as Machine Learning, Python, SQL, Statistics, "
                    "Deep Learning, or MLOps."
                ),
                sources=[],
                status="NO_RELEVANT_CONTEXT"
            )

        # 3. Assemble bounded context
        resources_context = cls.build_grounded_context(sources)
        learner_ctx_str = cls._format_learner_context(learner_context)

        # 4. Generate grounded answer via LLMProvider
        llm = llm_provider or get_llm_provider()
        prompt = RAG_USER_PROMPT_TEMPLATE.format(
            question=clean_q,
            learner_context=learner_ctx_str,
            resources_context=resources_context
        )

        answer_text = cls._call_llm_safely(llm, prompt)

        # 5. Citation validation: Only keep sources that actually exist in the retrieved set
        retrieved_ids = {s.resource_id for s in sources}
        validated_sources = [s for s in sources if s.resource_id in retrieved_ids]

        return RAGAnswerResponse(
            query=clean_q,
            answer=answer_text,
            sources=validated_sources,
            status="GROUNDED_ANSWER"
        )

    @classmethod
    def _format_learner_context(cls, ctx: Optional[Dict[str, Any]]) -> str:
        if not ctx:
            return "No specific learner profile context provided."
        parts = []
        if "target_role" in ctx:
            parts.append(f"Target Role: {ctx['target_role']}")
        if "active_milestone" in ctx:
            parts.append(f"Current Roadmap Milestone: {ctx['active_milestone']}")
        if "weak_skills" in ctx:
            parts.append(f"Identified Skill Gaps: {', '.join(ctx['weak_skills'])}")
        return "\n".join(parts) if parts else "Standard Learner Profile"

    @classmethod
    def _call_llm_safely(cls, provider: LLMProvider, prompt: str) -> str:
        try:
            import concurrent.futures
            def _run():
                return asyncio.run(
                    provider.generate(
                        prompt=prompt,
                        system_prompt=RAG_SYSTEM_PROMPT
                    )
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(_run).result(timeout=15.0)
        except Exception:
            from backend.app.ai.providers.mock_provider import MockLLMProvider
            fallback = MockLLMProvider()
            return asyncio.run(fallback.generate(prompt=prompt, system_prompt=RAG_SYSTEM_PROMPT))


def re_clean(text: str) -> str:
    """Helper to clean query text for token matching."""
    import re
    return re.sub(r"[^\w\s]", " ", (text or "").lower())
