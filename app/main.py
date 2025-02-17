from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.db import init_db
from app.routers.authentication import router
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.models import User
from app.routers.authentication import get_current_user

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

    app.include_router(router)

@app.get("/test/")
async def read_items(current_user: dict = Depends(get_current_user)):
    return {"token": "hoa ", 'user': current_user.username}

