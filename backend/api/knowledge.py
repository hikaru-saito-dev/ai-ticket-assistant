"""Knowledge CRUD API - /guilds/{guild_id}/knowledge."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_session
from backend.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse
from backend.services.guild_service import get_guild
from backend.services.knowledge_service import (
    create_knowledge,
    get_knowledge_by_id,
    list_knowledge,
    update_knowledge,
    delete_knowledge,
)

router = APIRouter(prefix="/guilds/{guild_id}/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeResponse])
async def list_guild_knowledge(
    guild_id: int,
    session: AsyncSession = Depends(get_session),
):
    """List all knowledge entries for a guild."""
    guild = await get_guild(session, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    items = await list_knowledge(session, guild_id)
    return [
        KnowledgeResponse(
            id=k.id,
            guild_id=k.guild_id,
            title=k.title,
            content=k.content,
            created_at=k.created_at.isoformat() if k.created_at else "",
        )
        for k in items
    ]


@router.post("", response_model=KnowledgeResponse)
async def create_guild_knowledge(
    guild_id: int,
    body: KnowledgeCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create knowledge entry. Fails if plan limit exceeded."""
    guild = await get_guild(session, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    knowledge = await create_knowledge(
        session, guild_id, body.title, body.content, plan=guild.plan
    )
    if not knowledge:
        raise HTTPException(
            status_code=403,
            detail="Knowledge entry limit exceeded for your plan. Please upgrade.",
        )
    return KnowledgeResponse(
        id=knowledge.id,
        guild_id=knowledge.guild_id,
        title=knowledge.title,
        content=knowledge.content,
        created_at=knowledge.created_at.isoformat() if knowledge.created_at else "",
    )


@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
async def get_guild_knowledge(
    guild_id: int,
    knowledge_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get knowledge entry by ID."""
    guild = await get_guild(session, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    knowledge = await get_knowledge_by_id(session, knowledge_id, guild_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return KnowledgeResponse(
        id=knowledge.id,
        guild_id=knowledge.guild_id,
        title=knowledge.title,
        content=knowledge.content,
        created_at=knowledge.created_at.isoformat() if knowledge.created_at else "",
    )


@router.put("/{knowledge_id}", response_model=KnowledgeResponse)
async def update_guild_knowledge(
    guild_id: int,
    knowledge_id: UUID,
    body: KnowledgeUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update knowledge entry."""
    guild = await get_guild(session, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    knowledge = await update_knowledge(
        session, knowledge_id, guild_id, title=body.title, content=body.content
    )
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return KnowledgeResponse(
        id=knowledge.id,
        guild_id=knowledge.guild_id,
        title=knowledge.title,
        content=knowledge.content,
        created_at=knowledge.created_at.isoformat() if knowledge.created_at else "",
    )


@router.delete("/{knowledge_id}", status_code=204)
async def delete_guild_knowledge(
    guild_id: int,
    knowledge_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Delete knowledge entry."""
    guild = await get_guild(session, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    deleted = await delete_knowledge(session, knowledge_id, guild_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Knowledge not found")
