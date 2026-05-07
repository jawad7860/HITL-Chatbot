"""LangGraph nodes for the chatbot.

Three logical nodes:

1. ``chat_node`` — invokes the LLM with tools bound. Produces either a final
   assistant message OR an AIMessage with `tool_calls` set.

2. ``human_review_node`` — calls ``interrupt()`` to pause execution and surface
   the pending tool call to the human. On resume:
     - approve → routes to ``tool_node``
     - reject  → injects a synthetic ToolMessage explaining the rejection and
                 routes back to ``chat_node`` so the LLM can respond gracefully.

3. ``tool_node`` — provided by ``langgraph.prebuilt.ToolNode`` and edges back
   to ``chat_node`` so the LLM can summarize tool results.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, Literal
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
from langgraph.types import Command, interrupt
from app.core.config import get_settings
from app.graph.prompts import SYSTEM_PROMPT
from app.graph.tools import ALL_TOOLS


logger = logging.getLogger(__name__)


def _build_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=0.3,
        max_tokens=1024,
    ).bind_tools(ALL_TOOLS)


# Cache the LLM client across invocations (cheap, but no need to rebuild).
_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = _build_llm()
    return _llm


async def chat_node(state: MessagesState) -> Dict[str, Any]:
    """Run the LLM. Always prepend the system prompt (it isn't stored in state)."""
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = await _get_llm().ainvoke(messages)
    return {"messages": [response]}


async def human_review_node(
    state: MessagesState,
) -> Command[Literal["tool_node", "chat_node"]]:
    """Pause for human approval of the pending tool call.

    The graph state was checkpointed before this node ran; ``interrupt()``
    raises a special exception that the runtime catches and surfaces to the
    caller. When the caller resumes the graph with ``Command(resume=...)``,
    execution continues here with ``decision`` set to that value.
    """
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        # Should not happen given our routing, but fail safely.
        logger.warning("human_review_node reached without a pending tool call")
        return Command(goto="chat_node")

    tool_call = last.tool_calls[0]

    decision = interrupt({
        "type": "tool_approval_request",
        "tool_call_id": tool_call["id"],
        "tool_name": tool_call["name"],
        "tool_args": tool_call["args"],
    })

    action = (decision or {}).get("action", "reject")

    if action == "approve":
        return Command(goto="tool_node")

    # Rejection path: synthesize a ToolMessage so the LLM sees the call as
    # resolved (otherwise it would re-emit the same tool_call on next turn)
    # and route back to chat_node for a graceful follow-up reply.
    rejection_message = ToolMessage(
        content=(
            "The user declined this tool call. Acknowledge politely and "
            "continue the conversation without the tool's output."
        ),
        tool_call_id=tool_call["id"],
        name=tool_call["name"],
    )
    return Command(
        goto="chat_node",
        update={"messages": [rejection_message]},
    )


def route_after_chat(state: MessagesState) -> Literal["human_review_node", "__end__"]:
    """Conditional edge: if the LLM emitted tool_calls, go to review; else end."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "human_review_node"
    return "__end__"
