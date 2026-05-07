"""POST /chat/{thread_id}/decision — approve or reject a pending tool call.

The actual graph resume happens in a FastAPI BackgroundTask, so this endpoint
returns immediately. The frontend polls GET /chat/{thread_id}/status until the
state transitions out of "processing".
"""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.api.deps import get_chat_service
from app.schemas import DecisionAcceptedResponse, DecisionRequest
from app.services import ChatService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def _resume_in_background(chat: ChatService, thread_id: str, action: str) -> None:
    """Worker function executed by FastAPI's BackgroundTasks runner."""
    try:
        await chat.resume_with_decision(thread_id, action)
    except Exception:  # noqa: BLE001
        logger.exception("Background resume failed for thread %s", thread_id)

@router.post("/{thread_id}/decision", response_model=DecisionAcceptedResponse)
async def post_decision(
    thread_id: str,
    body: DecisionRequest,
    background: BackgroundTasks,
    chat: ChatService = Depends(get_chat_service),
) -> DecisionAcceptedResponse:
    """Accept the user's approve/reject decision and schedule the graph resume.

    Validates that the thread is actually waiting for a decision before
    accepting; otherwise returns 409.
    """
    state = await chat.get_state_view(thread_id)
    if state["status"] != "pending_approval":
        raise HTTPException(
            status_code=409,
            detail=f"Thread is not awaiting approval (current status: {state['status']}).",
        )

    background.add_task(_resume_in_background, chat, thread_id, body.action)
    return DecisionAcceptedResponse(thread_id=thread_id)
