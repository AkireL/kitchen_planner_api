
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from tortoise.expressions import Q

from app.models import User
from app.services.user_service import UserService

user_router = APIRouter(prefix="/user")

@user_router.get('')
async def list_user():
    users = await UserService.list_user()

    return {
        "data": users
    }


@user_router.get("/search")
async def search_user(
    username: str | None = Query(None, description="username", min_length=1),
    email: str | None = Query(None, description="username", min_length=1),
):
    
    if not username and not email:
        raise HTTPException(status_code=400, detail="You must provide at least a value to search.")
    
    conditions = []

    if username:
        conditions.append(Q(username__icontains=username))
    if email:
        conditions.append(Q(email__icontains=email))

    if conditions:
        query = conditions[0] if len(conditions) == 1 else Q()
        for condition in conditions:
            query |= condition
    else:
        query = Q() 
        
    users = await User.filter(query).values("id", "username", "email", "fullname")
    return JSONResponse(content={"data": users})