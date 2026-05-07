"""POST /chat — send a user message into a (new or existing) conversation."""
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_chat_service
from app.schemas import ChatRequest, ChatStateResponse
from app.services import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatStateResponse)
async def post_message(
    body: ChatRequest,
    chat: ChatService = Depends(get_chat_service),
) -> ChatStateResponse:
    """Send a message. Runs the graph synchronously until either:

    - the conversation is complete (response ready), or
    - the graph hits an interrupt (tool call needs approval).

    Either way, returns the full current state so the frontend can render.
    """
    thread_id = body.thread_id or str(uuid4())
    try:
        state = await chat.send_message(thread_id, body.message)
    except Exception as e:  # noqa: BLE001 — surface as 500 with a clean payload
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {e}")
    return ChatStateResponse(**state)
