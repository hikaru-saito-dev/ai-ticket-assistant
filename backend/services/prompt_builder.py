"""Prompt builder - system + knowledge + message history."""

from backend.schemas.relay import PromptContext


def build_prompt_context(
    system_prompt: str,
    knowledge_chunks: list[dict],
    message_history: list[dict[str, str]],
) -> PromptContext:
    """Build prompt context for Phase 3 AI call."""
    return PromptContext(
        system_prompt=system_prompt,
        knowledge_chunks=knowledge_chunks,
        message_history=message_history[-8:],  # last 8 messages
    )
