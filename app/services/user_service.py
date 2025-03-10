from fastapi import HTTPException
from tortoise.expressions import Q

from app.models import RecipeUser, User
from app.schemas.recipe_schema import RecipeFilterSchema
from app.schemas.user_login_scheme import RegisterUserScheme
from app.services.recipe_service import RecipeService


class UserService:

    user: User

    def __init__(self, user: User):
        self.user = user

    @staticmethod
    async def list_user():
        return await User.filter()
    
    @staticmethod
    async def get_user(id):
        return await User.filter(id=id).first()


    @staticmethod
    async def get_user_by_username(username: str):
        return await User.filter(username=username).first()

    @staticmethod
    async def create(form_data: RegisterUserScheme, hash: str):
        user = await User.create(
            username=form_data.username,
            email=form_data.email,
            fullname=form_data.fullname,
            hashed_password=hash,
        )
        return user

    async def retrieve_users_to_shared_recipes(self, value: str):
        query =  User.filter(Q(username__icontains=value) | Q(email__icontains=value))
        
        query = query.exclude(id=self.user.id)
        
        query = query.values(
            "id",
            "username",
            "email",
            "fullname"
        )

        return await query

    async def shared_its_recipes(self, user_id: int, start_date, end_date):
        user_to_share_recipes = await UserService.get_user(user_id)

        if not user_to_share_recipes:
            raise HTTPException(
                status_code=404,
                detail="User does not found.")

        recipes = await RecipeService.filter_recipes(
            self.user.id, 
            RecipeFilterSchema(
                start_date = start_date,
                end_date = end_date,
            )
        )

        if recipes:
            user_recipes = [
                RecipeUser(user_id=user_to_share_recipes.id, recipe_id=recipe.id) 
                for recipe in recipes
            ]

            try:
                await RecipeUser.bulk_create(user_recipes)
            except Exception:
                return recipes

        return recipes