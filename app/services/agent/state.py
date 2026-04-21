from langgraph.graph import MessagesState


class State(MessagesState):
    user_id: int
    chat_id: int
