from datetime import date

from langchain.tools import tool
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    title: str = Field(min_length=1, max_length=255, description="Recipe title")
    ingredients: list[str] = Field(
        default_factory=list, description="List of ingredients for the recipe"
    )
    preparation: str = Field(min_length=1, description="Step-by-step preparation instructions")
    duration: str = Field(max_length=50, description="Estimated cooking time")
    schedule_at: date = Field(description="Date to schedule the recipe")


class ResponseModel(BaseModel):
    message: str = Field(description="User message when answer to user.")
    want_store: bool = Field(
        description="Indicate if the user wants to store the recipe.",
    )
    recipes: list[Recipe] | None = Field(
        default_factory=list,
        description="List of recipes. This field is only relevant if want_store is True.",
    )


@tool("get_weather", description="Get weather for a given city")
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


@tool("store_recipe", description="store a recipe when user wants to save it")
def store_recipe(data: list[Recipe]) -> str:
    """Store a recipe in the database."""
    print("Storing recipe:")
    print(str(data))
    return "Receta guardada exitosamente!"


tools = [get_weather, store_recipe]
