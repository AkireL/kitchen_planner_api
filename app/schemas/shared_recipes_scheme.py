from datetime import date

from pydantic import BaseModel, Field, validator


class SharedRecipesScheme(BaseModel):
    user_id: int = Field()
    start_date: date
    end_date: date

    @validator('end_date')
    def check_end_date(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('end_date must be greater than start_date')
        return v