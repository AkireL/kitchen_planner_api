
from typing import Any

from fastapi.responses import JSONResponse

from app.models import Recipe


class RecipeResource:
    @staticmethod
    def to_dict(recipe: Recipe) -> dict[str, Any]:
        return {
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "preparation": recipe.preparation,
            "duration": recipe.duration,
            "schedule_at": recipe.schedule_at.isoformat(),
            "user_id": recipe.user_id,
        }

    @staticmethod
    def collection(
        recipes: list,
        status_code: int = 200
    ) -> JSONResponse:

        data = []

        if recipes:
            data = [RecipeResource.to_dict(recipe) for recipe in recipes]

        return JSONResponse(
            content={
                "data": data,
            },
            status_code=status_code
        )

    @staticmethod
    def response(recipe: Recipe, status_code: int = 200) -> JSONResponse:

        return JSONResponse(
            content={
                "data": RecipeResource.to_dict(recipe),
            },
            status_code=status_code
        )
