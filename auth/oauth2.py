from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from routes import authuser_route

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "c8bf81a36968581fcb95cdec6ff8ee92"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


# Encoding the token to be used by the current user
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = (
            datetime.utcnow() + expires_delta
        )  # set expiration if expires_delta argument is provided
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )  # set expiration if expires_delta argument is not provided
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# function to fetch the user with it's credentials displayed
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # decode the payload via the token obtained from that current user
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = authuser_route.get_user_by_username(
        username, db
    )  # finding that specific user

    if user is None:
        raise credentials_exception

    return user
