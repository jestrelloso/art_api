import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.hash import Hash
from models import gallery_model
from schemas import gallery_schema

router = APIRouter(prefix="/api/artist", tags=["Artist"])


# Route for registering an artist
@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_artist(
    request: gallery_schema.ArtistSchema, db: Session = Depends(get_db)
):
    try:
        new_authenticated_user = gallery_model.Artist(
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
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[gallery_schema.ArtistDisplay],
)
async def get_all_artists(
    db: Session = Depends(get_db),
):
    try:
        users = db.query(gallery_model.Artist).all()
        if users is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return users
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Route for getting a single artist
@router.get("/{artist_id}", response_model=gallery_schema.ArtistDisplay)
async def get_single_artist(user_id: str, db: Session = Depends(get_db)):
    try:
        user = (
            db.query(gallery_model.Artist)
            .filter(gallery_model.Artist.id == user_id)
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
@router.put("/{artist_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_artist(
    request: gallery_schema.ArtistSchemaUpdate,
    user_id: str,
    db: Session = Depends(get_db),
):
    try:
        user_query = db.query(gallery_model.Artist).filter(
            gallery_model.Artist.id == user_id
        )
        if user_query.first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        user_query.update(
            {
                gallery_model.Artist.username: request.username,
                gallery_model.Artist.password: Hash.bcrypt(request.password),
            }
        )
        db.commit()
        return {"Message": "Artist Updated", "Artist": user_query.first()}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while updating the user!",
        )


# Route for deleting
@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(artist_id: str, db: Session = Depends(get_db)):
    try:
        user_query = db.query(gallery_model.Artist).filter(
            gallery_model.Artist.id == artist_id
        )
        user = user_query.first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {artist_id} not found",
            )
        db.delete(user)
        db.commit()
        return {"Status": "Success", "Message": "User deleted successfully!"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with an ID of {artist_id} does not exist!",
        )


def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = (
        db.query(gallery_model.Artist)
        .filter(gallery_model.Artist.username == username)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found",
        )
    return user
