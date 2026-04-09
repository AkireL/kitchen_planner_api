from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.graph import MessagesState

from app.services.agent.nodes.chef.prompt import prompt
from app.services.agent.nodes.chef.tools import tools


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: int
    thread_id: int


model = ChatOpenRouter(
    model="openai/gpt-oss-20b",
    temperature=0.5,
)


class State(MessagesState):
    user_id: int
    chat_id: int


def node(state: State):
    history = state["messages"]
    thread_id = state.get("thread_id")
    id = state.get("user_id")

    last_user_message = history[-1].content

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
    )

    config = {"configurable": {"thread_id": thread_id}}

    # Falta mandarle todo el contexto, no solo el último mensaje

    response = agent.invoke(
        {"messages": [{"role": "user", "content": last_user_message}]},
        config,
        context=Context(user_id=id, thread_id=thread_id),
    )

    ai_response = response["messages"][-1].content

    return {"messages": [AIMessage(content=ai_response)]}
