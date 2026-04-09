import os
from contextlib import asynccontextmanager
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.db import init_db
from app.routers.authentication_router import auth_router
from app.routers.recipe_router import recipe_router
from app.routers.shared_recipes_router import shared_recipe_router
from app.routers.user_router import user_router

DB_URI = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}?sslmode=disable"
)

_checkpointer: AsyncPostgresSaver | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(app)
    global _checkpointer
    conn = await psycopg.AsyncConnection.connect(DB_URI)
    await conn.set_autocommit(True)
    _checkpointer = AsyncPostgresSaver(conn)
    await _checkpointer.setup()

    from app.routers.chat_router import chat_router

    app.include_router(chat_router)
    app.include_router(auth_router)
    app.include_router(recipe_router)
    app.include_router(user_router)
    app.include_router(shared_recipe_router)
    yield


async def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialized. Make sure lifespan is running.")
    return _checkpointer


CheckpointerDep = Annotated[AsyncPostgresSaver, Depends(get_checkpointer)]
