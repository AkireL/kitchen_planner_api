import os
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.postgres import PostgresSaver

from app.services.agent.nodes.chef.prompt import prompt
from app.services.agent.nodes.chef.tools import tools


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str


model = ChatOpenRouter(
    model="openai/gpt-oss-20b",
    temperature=0.5,
)


def chat(user_id: str, thread_id: str, user_prompt: str):
    db_url = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}?sslmode=disable"
    )

    with PostgresSaver.from_conn_string(str(db_url)) as checkpointer:
        # checkpointer.setup()

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
            middleware=[
                SummarizationMiddleware(
                    model=model, trigger=("tokens", 4000), keep=("messages", 20)
                )
            ],
            checkpointer=checkpointer,
        )

        config = {"configurable": {"thread_id": thread_id}}

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_prompt}]},
            config,
            context=Context(user_id=user_id),
        )

        return response["messages"][-1].content


# chat(
#     user_id="123",
#     thread_id="thread_123",
#     user_prompt="me gusta la receta de pollo"
# )
