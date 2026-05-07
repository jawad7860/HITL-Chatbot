"""Graph state.

Uses the built-in ``MessagesState`` (which has a single ``messages`` field
with an ``add_messages`` reducer). Pending tool calls live on the last
``AIMessage.tool_calls`` — no extra state needed.
"""
from langgraph.graph import MessagesState

AgentState = MessagesState

__all__ = ["AgentState"]
