from datetime import date

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, Field

from app.services.agent.nodes.chef.services.recipe_store_adapter import RecipeStoreAdapter
from app.services.agent.state import State


class Recipe(BaseModel):
    title: str = Field(min_length=1, max_length=255, description="Recipe title")
    ingredients: list[str] = Field(
        default_factory=list, description="List of ingredients for the recipe"
    )
    preparation: str = Field(min_length=1, description="Step-by-step preparation instructions")
    duration: str = Field(max_length=50, description="Estimated cooking time")
    schedule_at: date = Field(description="Date to schedule the recipe")

@tool("store_recipe", description="store a recipe list when user wants to save it")
async def store_recipe(data: list[Recipe], runtime: ToolRuntime[None, State]) -> str:
    """Store a recipe in the database."""
    adapter = RecipeStoreAdapter()
    user_id = runtime.state.user_id

    return await adapter.store(user_id, data)


tools = [store_recipe]
