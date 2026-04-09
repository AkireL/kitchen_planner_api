from typing import TypedDict

from langgraph.graph import END, START, MessagesState, StateGraph

from app.services.agent.nodes.chef.node import node


class State(MessagesState):
    user_id: int


def make_graph(config: TypedDict):
    checkpointer = config.get("checkpointer", None)

    builder = StateGraph(State)
    builder.add_node("chef", node)

    builder.add_edge(START, "chef")
    builder.add_edge("chef", END)

    return builder.compile(checkpointer=checkpointer)
