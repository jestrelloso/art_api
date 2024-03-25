import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.hash import Hash
from models import authuser_model
from schemas import authuser_schema

router = APIRouter(prefix="/api/auth", tags=["authuser"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(
    request: authuser_schema.AuthSchema, db: Session = Depends(get_db)
):
    try:
        new_authenticated_user = authuser_model.AuthUser(
            id=str(uuid.uuid4()),
            username=request.username,
            password=Hash.bcrypt(request.password),
        )
        db.add(new_authenticated_user)
        db.commit()
        db.refresh(new_authenticated_user)
        return {"Registration Complete", new_authenticated_user}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occured while creating the user!",
        )


def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = (
        db.query(authuser_model.AuthUser)
        .filter(authuser_model.AuthUser.username == username)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found",
        )
    return user
