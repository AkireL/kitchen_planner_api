from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.recipe_schema import RecipeCreateScheme, RecipeFilterSchema
from app.services.recipe_service import RecipeService

recipe_router = APIRouter(prefix="/recipes")

@recipe_router.get('/')
async def filter_recipes(filters: RecipeFilterSchema=Body(default=None)):
    recipes = await RecipeService.filter_recipes(filters)

    if not recipes:
        raise HTTPException(status_code=404, detail="No found recipes")

    return [{
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "preparation": recipe.preparation,
        "duration": recipe.duration,
        "schedule_at": recipe.schedule_at.isoformat(),
    } for recipe in recipes]

    
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