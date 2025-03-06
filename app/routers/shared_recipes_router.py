from typing import Annotated

from fastapi import APIRouter, Depends

from app.models import User
from app.schemas.shared_recipes_scheme import SharedRecipesScheme
from app.services.auth_service import AuthService
from app.services.user_service import UserService

shared_recipe_router = APIRouter(
    prefix="/recipes", 
    dependencies=[Depends(AuthService.get_current_user)]
)

@shared_recipe_router.post('/share')
async def shared(
    user: Annotated[User, Depends(AuthService.get_current_user)],
    data: SharedRecipesScheme
):

    userService = UserService(user)

    recipes = await userService.shared_its_recipes(data.user_id, data.start_date, data.end_date)

    return {
        "shared_recipes": recipes,
    }
