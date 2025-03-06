from app.models import User
from app.schemas.user_login_scheme import RegisterUserScheme


class UserService:

    @staticmethod
    async def list_user():
        return await User.filter()
    
    @staticmethod
    async def exists_user(id):
        return await User.filter(id=id).first()


    @staticmethod
    async def get_user_by_username(username: str):
        return await User.filter(username=username).first()

    @staticmethod
    async def create(form_data: RegisterUserScheme, hash: str):
        user = await User.create(
            username=form_data.username,
            email=form_data.email,
            fullname=form_data.fullname,
            hashed_password=hash,
        )
        return user
