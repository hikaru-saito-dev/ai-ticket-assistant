"""Pydantic models for relay endpoint."""

from pydantic import BaseModel, Field


class RelayRequest(BaseModel):
    """Request payload for message relay."""

    guild_id: str = Field(..., description="Discord guild (server) ID")
    channel_id: str = Field(..., description="Discord channel ID")
    user_id: str = Field(..., description="Discord user ID who sent the message")
    content: str = Field(..., description="Message content")
    message_id: str | None = Field(None, description="Discord message ID (optional)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "guild_id": "123456789012345678",
                "channel_id": "987654321098765432",
                "user_id": "111222333444555666",
                "content": "Hello, I need help!",
                "message_id": "999888777666555444",
            }
        }


class RelayResponse(BaseModel):
    """Response payload for message relay."""

    reply: str = Field(..., description="AI response message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "reply": "AI is thinking... (Phase 1 placeholder)",
            }
        }

