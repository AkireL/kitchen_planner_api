from app.models import Recipe
from app.schemas.recipe_schema import RecipeCreateScheme


class RecipeService:

    @staticmethod
    async def get_recipes(start_date, end_date):
        return await Recipe.filter(schedule_at__range=(start_date, end_date)).all()
    
    @staticmethod
    async def get_recipe(id):
        return await Recipe.filter(id=id).first()
    
    @staticmethod
    async def create_recipe(data: RecipeCreateScheme):
        recipe = Recipe(
            title=data.title,
            ingredients=data.ingredients,
            preparation=data.preparation,
            duration=data.duration,
            schedule_at=data.schedule_at
        )
        
        await recipe.save()
        return recipe
    
    @staticmethod
    async def update_recipe(id, data: RecipeCreateScheme):
        recipe = await Recipe.filter(id=id).first()
        if not recipe:
            return None

        if data.title:
            recipe.title = data.title
        if data.ingredients:
            recipe.ingredients = data.ingredients
        if data.preparation:
            recipe.preparation = data.preparation
        if data.duration:
            recipe.duration = data.duration
        if data.schedule_at:
            recipe.schedule_at = data.schedule_at
        
        recipe.save()
        return recipe
    
    @staticmethod
    async def delete_recipe(id):
        recipe = Recipe.filter(id = id).first()

        if not recipe:
            return False
        recipe.delete()

        return True

