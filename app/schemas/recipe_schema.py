from datetime import date

from fastapi import Query
from pydantic import BaseModel, Field


class RecipeCreateScheme(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    ingredients: list[str] | None = Field(default_factory=list)
    preparation: str | None = Field(min_length=1, default=None)
    duration: str | None = Field(default=None, max_length=50)
    schedule_at: date


class RecipeFilterSchema(BaseModel):
    title: str | None = Query(None, description="Filter by title")
    duration: str | None = Query(None, description="Filter by duration")
    schedule_at: date | None = Query(None, description="Filter by schedule_at")
    start_date: date | None = Query(None, description="Filter by start_date")
    end_date: date | None = Query(None, description="Filter by end date")