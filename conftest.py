from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise


@asynccontextmanager
async def lifespan_test(app: FastAPI):
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def client():
    from app.db import init_db
    from app.main import create_application

    test_app = create_application(lifespan_func=lifespan_test)
    init_db(test_app, db_url="sqlite://:memory:")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac
