from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.models import Hash, User

auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user(username: str):
    return await User.filter(username=username).first()

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    hash = await Hash.filter(user=user).first()
    if not user or not verify_password(password, hash.hashed_password):
        return None
    return user

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_404,
                detail="Not exists"
            )
        user = await get_user(username)
        request.state.user = user
        return user
    except JWTError  as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from err

@auth_router.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await User.filter(username= form_data.username).first()

    if  user is not None:
        return JSONResponse(status_code=400, content="Already registered user")
    
    hashed_password = get_password_hash(form_data.password)
    user = await User.create(username=form_data.username, email=form_data.username)
    await Hash.create(user=user, hashed_password=hashed_password)
    return {"message": "Successfully registered user"}

@auth_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        return JSONResponse(status_code=401, content="Incorrect credentials")
    
    access_token = create_access_token(
        {"sub": user.username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user