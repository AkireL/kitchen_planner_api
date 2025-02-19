from app.models import Recipe
from app.schemas.recipe_schema import RecipeCreateScheme, RecipeFilterSchema


class RecipeService:

    @staticmethod
    async def get_recipe(id):
        return await Recipe.filter(id=id).first()
    
    @staticmethod
    async def create_recipe(data: RecipeCreateScheme):
        recipe = Recipe(title=data.title, schedule_at=data.schedule_at)
        
        if data.ingredients:
            recipe.ingredients = data.ingredients
        if data.preparation:
            recipe.preparation = data.preparation
        if data.duration:
            recipe.duration = data.duration
        
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
        
        await recipe.save()
        return recipe
    
    @staticmethod
    async def delete_recipe(id):
        recipe = await Recipe.filter(id=id).first()

        if not recipe:
            return False
        
        await recipe.delete()
        return True

    @staticmethod
    async def filter_recipes(filters: RecipeFilterSchema, offset: int, per_page: int):
        query = RecipeService.scope_filter(filters)
        query = query.limit(per_page).offset(offset)
        return await query

    @staticmethod
    async def get_count_recipes_to_filter(filters: RecipeFilterSchema):
        query = RecipeService.scope_filter(filters)
        query = query.count()

        return await query


    @staticmethod
    def scope_filter(filters: RecipeFilterSchema):
        if filters is None:
            return Recipe.all().count()

        query = Recipe.all()

        if filters.title:
            query = query.filter(title__icontains=filters.title)
        if filters.duration:
            query = query.filter(duration=filters.duration)
        if filters.schedule_at:
            query = query.filter(schedule_at=filters.schedule_at)
        if filters.start_date and filters.end_date:
            query = query.filter(
                schedule_at__gte=filters.start_date,
                schedule_at__lte=filters.end_date
            )
        return query