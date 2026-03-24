import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "SOME_SECRET_VALUE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str):
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "iat": now,
        "nbf": now,
        "exp": expire,
        "iss": "your-app",
        "aud": "your-users"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="your-users",
            issuer="your-app"
        )
    except JWTError:
        return None