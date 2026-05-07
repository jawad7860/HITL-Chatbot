"""Pydantic schemas for the chat API."""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class PendingApproval(BaseModel):
    tool_call_id: str
    tool_name: str
    tool_display_name: str
    tool_args: Dict[str, Any] = Field(default_factory=dict)


# ---- Requests ---------------------------------------------------------------


class ChatRequest(BaseModel):
    thread_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. Omit to start a new conversation.",
    )
    message: str = Field(..., min_length=1, max_length=8000)


class DecisionRequest(BaseModel):
    action: Literal["approve", "reject"]


# ---- Responses --------------------------------------------------------------


Status = Literal["empty", "completed", "pending_approval", "processing"]


class ChatStateResponse(BaseModel):
    thread_id: str
    status: Status
    messages: List[Message] = Field(default_factory=list)
    pending_approval: Optional[PendingApproval] = None


class DecisionAcceptedResponse(BaseModel):
    thread_id: str
    status: Literal["processing"] = "processing"
    detail: str = "Decision accepted; resuming graph in background."
