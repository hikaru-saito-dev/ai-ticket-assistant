"""Knowledge base schemas."""

from uuid import UUID
from pydantic import BaseModel, Field


class KnowledgeCreate(BaseModel):
    """Create knowledge entry."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)


class KnowledgeUpdate(BaseModel):
    """Update knowledge entry."""

    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = Field(None, min_length=1)


class KnowledgeResponse(BaseModel):
    """Knowledge entry response."""

    id: UUID
    guild_id: int
    title: str
    content: str
    created_at: str

    class Config:
        from_attributes = True
