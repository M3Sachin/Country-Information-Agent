"""
LangGraph workflow for Country Info Agent.
"""

from langgraph.graph import StateGraph, END

from country_info_agent.agents.state import AgentState
from country_info_agent.agents.nodes import (
    intent_node,
    tool_invocation_node,
    synthesis_node,
)


def create_graph():
    """
    Creates the LangGraph workflow for the Country Info Agent.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("intent", intent_node)
    workflow.add_node("tool", tool_invocation_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.set_entry_point("intent")

    workflow.add_edge("intent", "tool")
    workflow.add_edge("tool", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()
