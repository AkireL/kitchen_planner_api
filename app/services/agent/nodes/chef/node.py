from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_openrouter import ChatOpenRouter

from app.services.agent.nodes.chef.prompt import prompt
from app.services.agent.nodes.chef.tools import tools
from app.services.agent.state import State


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: int
    thread_id: int


model = ChatOpenRouter(
    model="openai/gpt-oss-20b",
    temperature=0.5,
)

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=prompt,
)


def node(state: State):
    new_state: State = {}
    thread_id = state.get("thread_id")
    id = state.get("user_id")

    response = agent.invoke(
        # {"messages": [{"role": "user", "content": last_user_message}]},
        {"messages": state.get("messages")},
        context=Context(user_id=id, thread_id=thread_id),
    )

    ai_message = AIMessage(content=response["messages"][-1].content)

    new_state["messages"] = [ai_message]

    return new_state
