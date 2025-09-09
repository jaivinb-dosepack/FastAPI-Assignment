from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def encrypt_password(password: str):
        return pwd_context.hash(password)