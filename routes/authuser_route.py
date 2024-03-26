import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.hash import Hash
from models import gallery_model
from schemas import gallery_schema

router = APIRouter(prefix="/api/auth", tags=["Artist"])


# Route for registering an artist
@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_artist(
    request: gallery_schema.AuthSchema, db: Session = Depends(get_db)
):
    try:
        new_authenticated_user = gallery_model.AuthUser(
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


# Route for getting all registered artists
@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[gallery_schema.UserDisplay]
)
async def get_all_artists(db: Session = Depends(get_db)):
    try:
        users = db.query(gallery_model.AuthUser).all()
        if users is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return users
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Route for getting a single artist
@router.get("/{user_id}", response_model=gallery_schema.UserDisplay)
async def get_single_artist(user_id: str, db: Session = Depends(get_db)):
    try:
        user = (
            db.query(gallery_model.AuthUser)
            .filter(gallery_model.AuthUser.id == user_id)
            .first()
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found!",
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found!"
        )


# Route for updating
@router.put("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_artist(
    request: gallery_schema.AuthSchemaUpdate,
    user_id: str,
    db: Session = Depends(get_db),
):
    try:
        user_query = db.query(gallery_model.AuthUser).filter(
            gallery_model.AuthUser.id == user_id
        )
        if user_query.first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        user_query.update(
            {
                gallery_model.AuthUser.username: request.username,
                gallery_model.AuthUser.password: Hash.bcrypt(request.password),
            }
        )
        db.commit()
        return {"Message": "User Updated", "User": user_query.first()}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while updating the user!",
        )


# Route for deleting
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(user_id: str, db: Session = Depends(get_db)):
    try:
        user_query = db.query(gallery_model.AuthUser).filter(
            gallery_model.AuthUser.id == user_id
        )
        user = user_query.first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        user_query.delete(synchronize_session=False)
        db.commit()
        return {"Status": "Success", "Message": "User deleted successfully!"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with an ID of {user_id} does not exist!",
        )


def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = (
        db.query(gallery_model.AuthUser)
        .filter(gallery_model.AuthUser.username == username)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found",
        )
    return user
