from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi.errors import RateLimitExceeded

from app.db import init_db
from app.rate_limit import config_rate_limit
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
    config_rate_limit(app)

    app.include_router(auth_router)
    app.include_router(recipe_router)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(
        status_code=429,
        detail="Too many requests. Please try again later.",
    )