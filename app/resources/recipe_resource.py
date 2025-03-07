
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
            "user_id": recipe.user.id,
        }

    @staticmethod
    def collection(
        recipes: list,
        page: int,
        per_page: int,
        total: int,
        status_code: int = 200
    ) -> JSONResponse:
        total_pages = (total + per_page - 1) // per_page

        data = []

        if recipes:
            data = [RecipeResource.to_dict(recipe) for recipe in recipes]

        return JSONResponse(
            content={
                "data": data,
                "meta": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                },
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
