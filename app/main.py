from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.config.app import ORIGINS
from app.db import init_db
from app.rate_limit import config_rate_limit
from app.routers.authentication_router import auth_router
from app.routers.recipe_router import recipe_router

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_application() -> FastAPI:
    application = FastAPI(
        title="Recipes API",
        description="Documentation",
        version="1.0.0",
        contact={
        "name": "Erika Basurto",
        "url": "https://www.linkedin.com/in/erika-basurto/",
        "email": "iamdleonor@gmail.com",
    },
    )
    return application

app = create_application()
config_rate_limit(app)
init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")

    app.include_router(auth_router)
    app.include_router(recipe_router)