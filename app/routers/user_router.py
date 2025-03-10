from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.models import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users")

@user_router.get("")
async def search_user(
    user: Annotated[User, Depends(AuthService.get_current_user)],
    username: str = Query(None, description="username", min_length=1),
):
    userService = UserService(user)
    users = await userService.retrieve_users_to_shared_recipes(username)
    
    return JSONResponse(content={"data": users})
