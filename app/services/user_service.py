from app.models import Hash, User
from app.schemas.user_login_scheme import RegisterUserScheme


class UserService:

    @staticmethod
    async def get_user_by_username(username: str):
        return await User.filter(username=username).first()

    @staticmethod
    async def create(form_data: RegisterUserScheme):
        user = await User.create(
            username=form_data.username,
            email=form_data.email,
            fullname=form_data.fullname,
        )
        return user

    @staticmethod
    async def saveHash(user: User, hashed_password: str):
        return await Hash.create(user=user, hashed_password=hashed_password)

