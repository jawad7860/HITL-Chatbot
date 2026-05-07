"""Build and compile the LangGraph state graph."""
from __future__ import annotations
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from app.graph.nodes import chat_node, human_review_node, route_after_chat
from app.graph.state import AgentState
from app.graph.tools import ALL_TOOLS


def build_graph(checkpointer: BaseCheckpointSaver):
    """Assemble nodes + edges and compile with the given checkpointer.

    Flow:
        START → chat_node
                  ↓
          (tool_calls?)
            ↓ yes        ↓ no
        human_review     END
            ↓                                  Command(goto)
        approve → tool_node → chat_node (loop)
        reject  → chat_node (with ToolMessage explaining rejection)
    """
    builder = StateGraph(AgentState)

    builder.add_node("chat_node", chat_node)
    builder.add_node("human_review_node", human_review_node)
    builder.add_node("tool_node", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "chat_node")
    builder.add_conditional_edges(
        "chat_node",
        route_after_chat,
        {"human_review_node": "human_review_node", "__end__": END},
    )
    # human_review_node uses Command(goto=...) so no added static edges.
    builder.add_edge("tool_node", "chat_node")

    return builder.compile(checkpointer=checkpointer)
