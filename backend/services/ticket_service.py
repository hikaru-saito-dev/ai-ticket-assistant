"""Ticket service - get or create ticket."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.ticket import Ticket


async def get_ticket(
    session: AsyncSession,
    guild_id: int,
    channel_id: int,
) -> Ticket | None:
    """Get existing open ticket by guild and channel."""
    result = await session.execute(
        select(Ticket).where(
            Ticket.guild_id == guild_id,
            Ticket.channel_id == channel_id,
            Ticket.status == "open",
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_ticket(
    session: AsyncSession,
    guild_id: int,
    channel_id: int,
) -> tuple[Ticket, bool]:
    """
    Get existing ticket or create new one.
    Returns (ticket, is_new). Caller must check daily limit BEFORE calling
    when ticket doesn't exist - this will create and consume a daily slot.
    """
    ticket = await get_ticket(session, guild_id, channel_id)
    if ticket:
        return ticket, False

    ticket = Ticket(
        guild_id=guild_id,
        channel_id=channel_id,
        status="open",
    )
    session.add(ticket)
    await session.flush()
    return ticket, True


async def get_ticket_by_channel(
    session: AsyncSession,
    guild_id: int,
    channel_id: int,
) -> Ticket | None:
    """Get ticket by guild and channel."""
    result = await session.execute(
        select(Ticket).where(
            Ticket.guild_id == guild_id,
            Ticket.channel_id == channel_id,
        )
    )
    return result.scalar_one_or_none()
