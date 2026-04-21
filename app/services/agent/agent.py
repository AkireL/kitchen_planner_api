from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.agent.nodes.chef.node import node
from app.services.agent.state import State


def make_graph(config: TypedDict):
    checkpointer = config.get("checkpointer", None)
    builder = StateGraph(State)
    builder.add_node("chef", node)
    builder.add_edge(START, "chef")
    builder.add_edge("chef", END)

    return builder.compile(checkpointer=checkpointer)
