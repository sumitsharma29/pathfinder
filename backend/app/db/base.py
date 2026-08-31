from datetime import datetime, timezone
import uuid
from typing import Optional, List, Union
from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import UserDefinedType


from sqlalchemy.types import UserDefinedType, TypeEngine, Float
from sqlalchemy.sql.operators import Operators


class Vector(UserDefinedType):
    """Vector type supporting PostgreSQL pgvector with native <=> distance operator."""
    cache_ok = True

    def __init__(self, dim: Optional[int] = None):
        super().__init__()
        self.dim = dim

    def get_col_spec(self, **kw):
        return "VECTOR"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            if isinstance(value, (list, tuple)):
                return list(value)
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            if isinstance(value, str):
                clean = value.strip("{}[]")
                if not clean:
                    return []
                return [float(x.strip()) for x in clean.split(",") if x.strip()]
            elif isinstance(value, (list, tuple)):
                return list(value)
            return value
        return process

    class Comparator(TypeEngine.Comparator):
        def cosine_distance(self, other: object) -> Operators:
            from sqlalchemy import cast
            bound = other if hasattr(other, "__clause_element__") else cast(other, self.expr.type)
            return self.op("<=>", return_type=Float)(bound)

        def l2_distance(self, other: object) -> Operators:
            from sqlalchemy import cast
            bound = other if hasattr(other, "__clause_element__") else cast(other, self.expr.type)
            return self.op("<->", return_type=Float)(bound)

        def max_inner_product(self, other: object) -> Operators:
            from sqlalchemy import cast
            bound = other if hasattr(other, "__clause_element__") else cast(other, self.expr.type)
            return self.op("<#>", return_type=Float)(bound)

    comparator_factory = Comparator


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 models."""
    pass


class TimestampMixin:
    """Standard timestamp mixin for mutable business entities."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )


class UUIDPrimaryKeyMixin:
    """UUID Primary Key mixin using PostgreSQL gen_random_uuid()."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
