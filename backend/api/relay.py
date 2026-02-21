"""Message relay endpoint."""

import logging
from fastapi import APIRouter, HTTPException
from backend.models.relay import RelayRequest, RelayResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/relay", tags=["relay"])


@router.post("", response_model=RelayResponse)
async def relay_message(request: RelayRequest) -> RelayResponse:
    """
    Relay a message from Discord bot to backend.

    In Phase 1, this endpoint simply logs the message and returns a placeholder response.
    Future phases will add AI processing, limit checks, and knowledge retrieval.

    Args:
        request: Relay request payload containing message details

    Returns:
        RelayResponse: Placeholder AI response

    Raises:
        HTTPException: If request validation fails
    """
    try:
        # Log the incoming message
        logger.info(
            f"Received message relay: guild={request.guild_id}, "
            f"channel={request.channel_id}, user={request.user_id}, "
            f"content_length={len(request.content)}"
        )

        # Phase 1: Return placeholder response
        # Future phases will:
        # 1. Validate ticket channel
        # 2. Check usage limits
        # 3. Retrieve relevant knowledge
        # 4. Call AI engine
        # 5. Log token usage

        response = RelayResponse(reply="AI is thinking... (Phase 1 placeholder)")

        logger.info(
            f"Returning response for guild={request.guild_id}, "
            f"channel={request.channel_id}"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing relay request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e

