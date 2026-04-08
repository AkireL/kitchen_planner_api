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
    # model="openai/gpt-4o-mini",
    model="openai/gpt-oss-20b",
    temperature=0.5,
)

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
            SummarizationMiddleware(model=model, trigger=("tokens", 4000), keep=("messages", 20))
        ],
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": "1"}}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "dame el clima"}]},
        config,
        context=Context(user_id="1"),
    )

    print(response["messages"][-1].content)
