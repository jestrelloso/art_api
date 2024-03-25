from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.hash import Hash
from auth import oauth2
from models import gallery_model

router = APIRouter(tags=["authentication"])


# token route
@router.post("/token", status_code=status.HTTP_201_CREATED)
async def get_token(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # find valid existing user in the authusers database
    user = (
        db.query(gallery_model.AuthUser)
        .filter(gallery_model.AuthUser.username == request.username)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password"
        )

    access_token = oauth2.create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "user_id": user.id,
        "username": user.username,
        "password": user.password,
    }
