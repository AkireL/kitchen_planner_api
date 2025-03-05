from typing import Annotated

from fastapi import APIRouter, Depends

from app.models import User
from app.schemas.shared_recipes_scheme import SharedRecipesScheme
from app.services.auth_service import AuthService

shared_recipe_router = APIRouter(
    prefix="/recipes", 
    dependencies=[Depends(AuthService.get_current_user)]
)

@shared_recipe_router.post('')
async def shared(
    user: Annotated[User, Depends(AuthService.get_current_user)],
    data: SharedRecipesScheme):

    return {
        user: user,
        data: data
    }
