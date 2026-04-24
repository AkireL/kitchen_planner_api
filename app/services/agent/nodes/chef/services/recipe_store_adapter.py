from __future__ import annotations

from dataclasses import dataclass

from app.schemas.recipe_schema import RecipeCreateScheme
from app.services.recipe_service import RecipeService


@dataclass(slots=True)
class RecipeStoreAdapter:
    async def store(self, user_id: int, recipes: list) -> str:
        stored = 0
        errors: list[str] = []

        for recipe in recipes:
            try:
                await self._store(user_id, recipe)
                stored += 1
            except Exception as exc:
                errors.append(f"{recipe.title}: {exc}")

        if errors and stored == 0:
            return "No se pudo guardar ninguna receta."

        if errors:
            return f"Se guardaron {stored} receta(s), pero hubo errores: {'; '.join(errors)}"

        return "Receta guardada exitosamente!"

    async def _store(self, user_id: int, recipe) -> None:
        data = RecipeCreateScheme(
            title=recipe.title,
            ingredients=recipe.ingredients,
            preparation=recipe.preparation,
            duration=recipe.duration,
            schedule_at=recipe.schedule_at,
        )
        await RecipeService.create_recipe(user_id, data)
