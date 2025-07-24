from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "kuchh_bhi_nahi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(date: dict):
    to_encode = date.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        playload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return playload
    except JWTError:
        return None