from typing import Annotated

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.user_service import UserService

user_router = APIRouter(prefix="/user")

@user_router.get('')
async def list_user():
    users = await UserService.list_user()

    return {
        "data": users
    }