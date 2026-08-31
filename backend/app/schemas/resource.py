import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ResourceSkillSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResourceItemResponse(BaseModel):
    """Resource item representation without exposing internal vector embeddings."""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    resource_type: str
    provider: Optional[str] = None
    url: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    quality_score: Optional[float] = None
    is_active: bool = True
    skills: List[ResourceSkillSummary] = []
    metadata_info: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ResourceDetailResponse(BaseModel):
    """Detailed resource view with associated skills and metadata."""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    resource_type: str
    provider: Optional[str] = None
    url: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    quality_score: Optional[float] = None
    is_active: bool = True
    skills: List[ResourceSkillSummary] = []
    metadata_info: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PaginatedResourcesResponse(BaseModel):
    items: List[ResourceItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
