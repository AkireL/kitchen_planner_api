from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import APIRouter
from app.models import User, Hash
import os

router = APIRouter()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = (int)(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 20))

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return await get_user(username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.post("/register")
async def register(username: str, password: str):
    user = await User.filter(username= username).first()

    if  user is not None:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")
    
    hashed_password = get_password_hash(password)
    user = await User.create(username=username, email=username)
    await Hash.create(user=user, hashed_password=hashed_password)
    return {"message": "Usuario registrado exitosamente"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token = create_access_token(
        {"sub": user.username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


