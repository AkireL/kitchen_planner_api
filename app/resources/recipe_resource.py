
from typing import Any

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
        }

    @staticmethod
    def collection(recipes: list) -> list[Recipe]:
        return [RecipeResource.to_dict(recipe) for recipe in recipes]

    @staticmethod
    def response(data: list, page: int, per_page: int, total: int) -> dict[str, Any]:
        total_pages = (total + per_page - 1) // per_page

        if data:
            data = RecipeResource.collection(data)

        return {
            "data": data,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }
        }