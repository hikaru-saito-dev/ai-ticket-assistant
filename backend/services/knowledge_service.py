"""Knowledge service - CRUD and similarity search."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.knowledge import Knowledge
from backend.schemas.plans import PLAN_LIMITS
from backend.utils.embeddings import embed_text, cosine_similarity


async def get_knowledge_count(session: AsyncSession, guild_id: int) -> int:
    """Count knowledge entries for guild."""
    result = await session.execute(
        select(Knowledge).where(Knowledge.guild_id == guild_id)
    )
    return len(result.scalars().all())


async def create_knowledge(
    session: AsyncSession,
    guild_id: int,
    title: str,
    content: str,
    plan: str = "free",
) -> Knowledge | None:
    """Create knowledge entry. Returns None if limit exceeded."""
    count = await get_knowledge_count(session, guild_id)
    limits = PLAN_LIMITS.get(plan.lower(), PLAN_LIMITS["free"])
    if count >= limits["knowledge_entries"]:
        return None

    embedding = embed_text(f"{title}\n{content}")
    knowledge = Knowledge(
        guild_id=guild_id,
        title=title,
        content=content,
        embedding=embedding,
    )
    session.add(knowledge)
    await session.flush()
    return knowledge


async def get_knowledge_by_id(
    session: AsyncSession,
    knowledge_id: uuid.UUID,
    guild_id: int,
) -> Knowledge | None:
    """Get knowledge entry by ID and guild."""
    result = await session.execute(
        select(Knowledge).where(
            Knowledge.id == knowledge_id,
            Knowledge.guild_id == guild_id,
        )
    )
    return result.scalar_one_or_none()


async def list_knowledge(session: AsyncSession, guild_id: int) -> list[Knowledge]:
    """List all knowledge entries for guild."""
    result = await session.execute(
        select(Knowledge).where(Knowledge.guild_id == guild_id).order_by(Knowledge.created_at)
    )
    return list(result.scalars().all())


async def update_knowledge(
    session: AsyncSession,
    knowledge_id: uuid.UUID,
    guild_id: int,
    title: str | None = None,
    content: str | None = None,
) -> Knowledge | None:
    """Update knowledge entry."""
    k = await get_knowledge_by_id(session, knowledge_id, guild_id)
    if not k:
        return None
    if title is not None:
        k.title = title
    if content is not None:
        k.content = content
        k.embedding = embed_text(f"{k.title}\n{k.content}")
    await session.flush()
    return k


async def delete_knowledge(
    session: AsyncSession,
    knowledge_id: uuid.UUID,
    guild_id: int,
) -> bool:
    """Delete knowledge entry. Returns True if deleted."""
    k = await get_knowledge_by_id(session, knowledge_id, guild_id)
    if not k:
        return False
    await session.delete(k)
    await session.flush()
    return True


async def search_knowledge(
    session: AsyncSession,
    guild_id: int,
    query: str,
    top_k: int = 3,
    plan: str = "free",
) -> list[Knowledge]:
    """Search knowledge by cosine similarity. Returns top_k entries."""
    limit = PLAN_LIMITS.get(plan.lower(), PLAN_LIMITS["free"])["knowledge_entries"]
    result = await session.execute(
        select(Knowledge).where(Knowledge.guild_id == guild_id)
    )
    all_k = list(result.scalars().all())
    if not all_k:
        return []

    query_embedding = embed_text(query)
    scored = []
    for k in all_k:
        if k.embedding:
            sim = cosine_similarity(query_embedding, k.embedding)
            scored.append((sim, k))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [k for _, k in scored[:top_k]]
