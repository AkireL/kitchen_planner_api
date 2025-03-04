from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config.auth import ALGORITHM, SECRET_KEY


class JWTService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
