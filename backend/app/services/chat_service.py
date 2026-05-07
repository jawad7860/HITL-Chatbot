"""Chat service.

Encapsulates all interactions with the compiled LangGraph: sending a new
message, resuming after a human decision, and reading current state.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from app.graph.tools import TOOL_DISPLAY_NAMES


logger = logging.getLogger(__name__)


def _config(thread_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def _serialize_messages(messages: List[Any]) -> List[Dict[str, Any]]:
    """Convert LangChain messages into JSON-friendly dicts for the frontend.

    Tool messages and tool_call AI messages are filtered out — the frontend
    only renders human-visible turns. Approval cards are derived separately
    from graph state, not from chat history.
    """
    out: List[Dict[str, Any]] = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            # Skip empty assistant messages whose only purpose was a tool_call.
            if isinstance(m.content, str) and m.content.strip():
                out.append({"role": "assistant", "content": m.content})
            elif isinstance(m.content, list):
                # Anthropic returns content blocks; extract text blocks only.
                text = "".join(
                    b.get("text", "") for b in m.content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
                if text.strip():
                    out.append({"role": "assistant", "content": text})
        # ToolMessage is intentionally not surfaced to the user.
    return out


class ChatService:
    """Orchestrates graph invocations for the API layer."""

    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph

    # ---- read-side ---------------------------------------------------------

    async def get_state_view(self, thread_id: str) -> Dict[str, Any]:
        """Return a snapshot of the conversation suitable for the frontend.

        Status is one of:
          - "completed"        — graph is idle, last message is the assistant's
          - "pending_approval" — graph is paused at human_review_node
          - "processing"       — graph is mid-execution (e.g. tool running)
          - "empty"            — no state yet for this thread
        """
        config = _config(thread_id)
        snapshot = await self.graph.aget_state(config)

        if not snapshot or not snapshot.values:
            return {
                "thread_id": thread_id,
                "status": "empty",
                "messages": [],
                "pending_approval": None,
            }

        messages = snapshot.values.get("messages", [])
        serialized = _serialize_messages(messages)

        # Detect interrupt
        pending_approval = self._extract_interrupt(snapshot)
        if pending_approval is not None:
            return {
                "thread_id": thread_id,
                "status": "pending_approval",
                "messages": serialized,
                "pending_approval": pending_approval,
            }

        # If graph has next steps queued but no interrupt, it's processing.
        if snapshot.next:
            return {
                "thread_id": thread_id,
                "status": "processing",
                "messages": serialized,
                "pending_approval": None,
            }

        return {
            "thread_id": thread_id,
            "status": "completed",
            "messages": serialized,
            "pending_approval": None,
        }

    @staticmethod
    def _extract_interrupt(snapshot) -> Optional[Dict[str, Any]]:
        """Pull the interrupt payload (if any) out of the graph snapshot."""
        for task in snapshot.tasks or []:
            interrupts = getattr(task, "interrupts", None) or []
            for interrupt_ in interrupts:
                value = getattr(interrupt_, "value", None)
                if isinstance(value, dict) and value.get("type") == "tool_approval_request":
                    return {
                        "tool_call_id": value.get("tool_call_id"),
                        "tool_name": value.get("tool_name"),
                        "tool_display_name": TOOL_DISPLAY_NAMES.get(
                            value.get("tool_name", ""), value.get("tool_name", "Unknown tool"),
                        ),
                        "tool_args": value.get("tool_args", {}),
                    }
        return None

    # ---- write-side --------------------------------------------------------

    async def send_message(self, thread_id: str, message: str) -> Dict[str, Any]:
        """Append a user message and run the graph until interrupt or end."""
        config = _config(thread_id)
        await self.graph.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )
        return await self.get_state_view(thread_id)

    async def resume_with_decision(
        self, thread_id: str, action: str
    ) -> Dict[str, Any]:
        """Resume an interrupted graph with the user's approve/reject choice."""
        if action not in {"approve", "reject"}:
            raise ValueError(f"Invalid action: {action!r}")

        config = _config(thread_id)
        await self.graph.ainvoke(
            Command(resume={"action": action}),
            config=config,
        )
        return await self.get_state_view(thread_id)
