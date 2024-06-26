import os
import shutil
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from auth.oauth2 import get_current_user
from models import gallery_model
from schemas import gallery_schema

router = APIRouter(prefix="/api/artwork", tags=["Artwork"])


# Route for creating an artwork
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_artwork(
    name: str,
    description: str,
    uploadfile: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_artist: gallery_schema.ArtistSchema = Depends(get_current_user),
):
    try:
        # Save the uploaded image to the specified directory
        image_path = f"images/{current_artist.id}_{uploadfile.filename}"
        with open(image_path, "wb") as image:
            shutil.copyfileobj(uploadfile.file, image)

        # Create a new Artwork instance with the provided data
        new_artwork = gallery_model.Artwork(
            name=name,
            description=description,
            image_url=image_path,  # Save the file path to the database
            artist_id=current_artist.id,
        )

        # Add the new artwork to the database session
        db.add(new_artwork)

        # Commit the transaction to save the artwork to the database
        db.commit()

        # Refresh the new artwork instance to populate any generated fields
        db.refresh(new_artwork)

        return {"New Artwork": new_artwork}
    except Exception as e:
        # If an error occurs, raise an HTTPException with status 400 and the error message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Route for reading all artworks
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[gallery_schema.ArtworkDisplay],
)
async def get_all_artworks(
    db: Session = Depends(get_db),
    current_artist: gallery_schema.ArtistSchema = Depends(get_current_user),
):
    try:
        artworks = (
            db.query(gallery_model.Artwork)
            .filter(gallery_model.Artwork.artist_id == current_artist.id)
            .all()
        )
        if artworks is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return artworks
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={e})


# Route for reading a single artwork
@router.get("/{artwork_id}", response_model=gallery_schema.ArtworkDisplay)
async def get_single_artwork(
    artwork_id: str,
    db: Session = Depends(get_db),
    current_artist: gallery_schema.ArtistSchema = Depends(get_current_user),
):
    try:
        artwork = (
            db.query(gallery_model.Artwork)
            .filter(
                gallery_model.Artwork.id == artwork_id,
                gallery_model.Artwork.artist_id == current_artist.id,
            )
            .first()
        )
        if artwork is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork {artwork_id} not found!",
            )
        return artwork
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork {artwork_id} not found!",
        )


# # Route for updating an artwork
@router.put("/{artwork_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_artwork(
    artwork_id: str,
    name: str,
    description: str,
    uploadfile: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_artist: gallery_schema.ArtistSchema = Depends(get_current_user),
):
    try:
        # fetch the artwork under the user that is logged in
        user_query = db.query(gallery_model.Artwork).filter(
            gallery_model.Artwork.id == artwork_id,
            gallery_model.Artwork.artist_id == current_artist.id,
        )
        # store the first fetched instance into a variable
        artwork = user_query.first()
        # error handling when none
        if artwork is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork with ID {artwork_id} not found!",
            )
        # if an image url under that artwork id exists
        if os.path.exists(artwork.image_url):
            os.remove(artwork.image_url)  # delete the image in that path

        # Save the uploaded image to the specified directory (to replace)
        image_path = f"images/{current_artist.id}_{uploadfile.filename}"
        with open(image_path, "wb") as image:
            shutil.copyfileobj(uploadfile.file, image)

        # update the fields
        user_query.update(
            {
                gallery_model.Artwork.name: name,
                gallery_model.Artwork.description: description,
                gallery_model.Artwork.image_url: image_path,
            }
        )
        db.commit()
        return {"Message": "Artwork Updated", "Artwork": user_query.first()}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occured while updating the user!",
        )


# Route for deleting an artwork
@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(
    artwork_id: str,
    db: Session = Depends(get_db),
    current_artist: gallery_schema.ArtistSchema = Depends(get_current_user),
):
    try:
        artwork = (
            db.query(gallery_model.Artwork)
            .filter(gallery_model.Artwork.id == artwork_id)
            .first()
        )
        if artwork is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork {artwork_id} not found!",
            )

        # deletion of instance in the image path
        if os.path.exists(artwork.image_url):
            os.remove(artwork.image_url)

        db.delete(artwork)
        db.commit()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork {artwork_id} not found!",
        )


# to retrieve and download an image via an endpoint
@router.get(
    "/download/{name}",
    response_class=FileResponse,
)
async def get_file(
    name: str, current_artist: gallery_schema.ArtistSchema = Depends(get_current_user)
):
    path = f"images/{name}"
    return path
