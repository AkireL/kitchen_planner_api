from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.config.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import Hash, User
from app.schemas.user_login_scheme import LogInScheme, RegisterUserScheme
from app.services.auth_service import AuthService
from app.services.user_service import UserService

auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@auth_router.post("/register")
async def register(form_data: RegisterUserScheme):
    user = await User.filter(
        username= form_data.username,
        email=form_data.email
    ).first()

    if  user is not None:
        return JSONResponse(status_code=400, content="Already registered user")
    
    hashed_password = AuthService.get_password_hash(form_data.password)
    user = await UserService.create(form_data)

    await UserService.saveHash(user, hashed_password)

    return {
        "message": "Successfully registered user", 
        "data": {
            "jwt": hashed_password,
            "user": user,
        }
    }

@auth_router.post("/token")
async def login(form_data: LogInScheme):
    user = await UserService.get_user_by_username(form_data.username)
    hash = await Hash.filter(user=user).first()

    if not user:
        return JSONResponse(status_code=401, content="Incorrect credentials")

    if not hash:
        return JSONResponse(status_code=401, content="Incorrect credentials")

    is_user_right = AuthService.verify_password(form_data.password, hash.hashed_password)
    
    if not is_user_right:
        raise HTTPException(
            status_code=404,
            detail="Incorrect credentials."
        )
    
    access_token = AuthService.create_access_token(
        {"sub": user.username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me")
async def read_users_me(current_user: dict = Depends(AuthService.get_current_user)):
    return current_user