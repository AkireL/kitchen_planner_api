from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from app.db import init_db
from app.routers.authentication import auth_router
from app.routers.recipe_router import recipe_router

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_application() -> FastAPI:
    application = FastAPI()
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    init_db(app)
    print("Database initialized successfully.")

    app.include_router(auth_router)
    app.include_router(recipe_router)