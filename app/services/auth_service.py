from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.services.jwt_service import JWTService
from app.services.user_service import UserService


class AuthService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @staticmethod
    async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
        try:
            payload = JWTService.decode_token(token)
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_404,
                    detail="Not exists"
                )
            user = await UserService.get_user_by_username(username)
            request.state.user = user
            return user
        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            ) from err