import bcrypt


class Password:

    @staticmethod
    def get_password_hash(password: str):
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        password_byte_enc = plain_password.encode('utf-8')
        return bcrypt.checkpw(
            password = password_byte_enc,
            hashed_password = hashed_password.encode("utf-8")
        )