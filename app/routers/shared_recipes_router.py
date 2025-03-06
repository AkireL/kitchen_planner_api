from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.models import RecipeUser, User
from app.schemas.recipe_schema import RecipeFilterSchema
from app.schemas.shared_recipes_scheme import SharedRecipesScheme
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeService
from app.services.user_service import UserService

shared_recipe_router = APIRouter(
    prefix="/recipes", 
    dependencies=[Depends(AuthService.get_current_user)]
)

@shared_recipe_router.post('/share')
async def shared(
    user: Annotated[User, Depends(AuthService.get_current_user)],
    data: SharedRecipesScheme):

    exist_user: bool = await UserService.exists_user(data.user_id)

    if not exist_user:
        raise HTTPException(
                status_code=422,
                detail="User does not found")
    
    recipes = await RecipeService.filter_recipes(
        user.id, 
        RecipeFilterSchema(
            start_date= data.start_date,
            end_date= data.end_date,
        )
    )

    if recipes:
        user_recipes = [
            RecipeUser(user_id=exist_user.id, recipe_id=recipe.id) 
            for recipe in recipes
        ]

    await RecipeUser.bulk_create(user_recipes)

    return {
        "message": recipes,
        "ids": user_recipes
    }
