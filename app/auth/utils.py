from passlib.context import CryptContext
from jose import jwt
import time, os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = os.getenv("SECRET_KEY", "secret")

def hash_password(p): return pwd_context.hash(p)
def verify_password(p, h): return pwd_context.verify(p, h)

def create_token(user_id):
    return jwt.encode(
        {"sub": user_id, "exp": time.time() + 86400},
        SECRET,
        algorithm="HS256"
    )
