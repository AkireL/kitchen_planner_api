from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models import User
from app.routers.authentication_router import get_current_user
from app.schemas.recipe_schema import RecipeCreateScheme, RecipeFilterSchema
from app.services.recipe_service import RecipeService

recipe_router = APIRouter(prefix="/recipes", dependencies=[Depends(get_current_user)])

@recipe_router.get('/')
async def filter_recipes(
    user: Annotated[User, Depends(get_current_user)],
    filters: RecipeFilterSchema=Depends(),
    page: int = Query(1, ge=1, description="Number page"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
):
    print(user)

    offset = (page - 1) * per_page

    recipes = await RecipeService.filter_recipes(
        filters,
        offset,
        per_page
    )
    total_recipes = await RecipeService.get_count_recipes_to_filter(filters)
    
    total_pages = (total_recipes + per_page - 1) // per_page

    if not recipes:
        raise HTTPException(status_code=404, detail="No found recipes")

    return {
        "data": [{
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "preparation": recipe.preparation,
            "duration": recipe.duration,
            "schedule_at": recipe.schedule_at.isoformat(),
        } for recipe in recipes],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total_recipes,
            "total_pages": total_pages,
        }
    }

    
@recipe_router.post('/')
async def create_recipe(data: RecipeCreateScheme):
    recipe = await RecipeService.create_recipe(data)

    return JSONResponse(content={
        'id': recipe.id,
        'title': recipe.title,
        'ingredients': recipe.ingredients,
        'preparation': recipe.preparation,
        'duration': recipe.duration,
        'schedule_at': recipe.schedule_at.isoformat()
    }, status_code=201)


@recipe_router.put('/{id}')
async def update_recipe(id, data: RecipeCreateScheme):
    if not data:
        return JSONResponse(content={'error': 'No fields to update'}, status_code=400)

    recipe = await RecipeService.update_recipe(id, data)

    if not recipe:
        return JSONResponse(content={'error': 'Recipe not found'}, status_code=404)

    return JSONResponse(content={
        'id': recipe.id,
        'title': recipe.title,
        'ingredients': recipe.ingredients,
        'preparation': recipe.preparation,
        'duration': recipe.duration,
        'schedule_at': recipe.schedule_at.isoformat()
    }, status_code=200)


@recipe_router.delete('/{id}')
async def delete_recipe(id):
    deleted = await RecipeService.delete_recipe(id)

    if deleted:
        return JSONResponse(content={"message": "Recipe deleted successfully"}, status_code=200)
    raise HTTPException(status_code=404, detail="Recipe not found")