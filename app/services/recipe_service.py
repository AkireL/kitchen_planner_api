from app.models import Recipe
from app.schemas.recipe_schema import RecipeCreateScheme, RecipeFilterSchema


class RecipeService:

    @staticmethod
    async def get_recipe(id):
        return await Recipe.filter(id=id).first()

    @staticmethod
    async def create_recipe(user_id: str, data: RecipeCreateScheme):
        recipe = Recipe(
            title=data.title,
            schedule_at=data.schedule_at,
            user_id = user_id
        )

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
    async def filter_recipes(
        user_id: str,
        filters: RecipeFilterSchema,
        offset: int=0,
        per_page: int=0
    ):
        query = RecipeService.scope_filter(user_id, filters)
        
        if per_page > 0 and offset > 0:
            query = query.limit(per_page).offset(offset)
        
        return await query

    @staticmethod
    async def get_count_recipes_to_filter(user_id, filters: RecipeFilterSchema):
        query = RecipeService.scope_filter(user_id, filters)
        query = query.count()

        return await query


    @staticmethod
    def scope_filter(user_id: str, filters: RecipeFilterSchema):
        if filters is None:
            return Recipe.all().count()

        query = Recipe.all()
        query = query.filter(user_id=user_id)

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