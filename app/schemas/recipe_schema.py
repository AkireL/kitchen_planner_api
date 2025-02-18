from datetime import date

from pydantic import BaseModel, Field


class RecipeCreateScheme(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    ingredients: list[str] | None = Field(default_factory=list)
    preparation: str = Field(min_length=1, default=None)
    duration: str | None = Field(default=None, max_length=50)
    schedule_at: date
