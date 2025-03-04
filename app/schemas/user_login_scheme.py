import re

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, validator
    

class LogInScheme(BaseModel):
    password: str = Field(min_length=8)
    username: str = Field(min_length=4)

    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[a-z]', v):
            raise HTTPException(
                status_code=422,
                detail="Password must contain at least one lowercase letter.")
        if not re.search(r'[A-Z]', v):
            raise HTTPException(
                status_code=422,
                detail="Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', v):
            raise HTTPException(
                status_code=422,
                detail="Password must contain at least one number.")
        return v

class RegisterUserScheme(LogInScheme):
    full_name: str = Field(max_length=255)
    email: EmailStr
    

