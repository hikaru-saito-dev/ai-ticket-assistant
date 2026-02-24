"""FastAPI dependencies for Redis and other app-state resources."""

from typing import Annotated
from fastapi import Request
from redis.asyncio import Redis


def get_redis(request: Request) -> Redis:
    """Get Redis client from app state."""
    return request.app.state.redis
