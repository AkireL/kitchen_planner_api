from datetime import date

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator

from app.services.user_service import UserService


class SharedRecipesScheme(BaseModel):
    user_id: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date


    @validator('user_id')
    async def validate_exist_user(cls, v):
        if await UserService.exists_user(v):
            return v
        raise HTTPException(
                status_code=422,
                detail="User does not exists")
    
    @validator('end_date')
    def check_end_date(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('end_date must be greater than start_date')
        return v