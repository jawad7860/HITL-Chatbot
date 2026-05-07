"""GET /chat/{thread_id}/status — poll for current conversation state.

Used by the frontend after sending a decision: it polls this endpoint until
the status transitions out of "processing".
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_chat_service
from app.schemas import ChatStateResponse
from app.services import ChatService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/{thread_id}/status", response_model=ChatStateResponse)
async def get_status(
    thread_id: str,
    chat: ChatService = Depends(get_chat_service),
) -> ChatStateResponse:
    """Return the current state of a thread (messages + status + pending approval)."""
    state = await chat.get_state_view(thread_id)
    return ChatStateResponse(**state)
