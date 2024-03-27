import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from models import gallery_model

router = APIRouter(prefix="/api/artwork", tags=["Artwork"])


# Route for creating an artwork
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_artwork(
    name: str,
    description: str,
    artist_id: str,
    uploadfile: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Save the uploaded image to the specified directory
        image_path = f"images/{uploadfile.filename}"
        with open(image_path, "wb") as image:
            shutil.copyfileobj(uploadfile.file, image)

        # Create a new Artwork instance with the provided data
        new_artwork = gallery_model.Artwork(
            name=name,
            description=description,
            image_url=image_path,  # Save the file path to the database
            user_id=artist_id,
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


# to upload files that has a .jpeg, .png file types
@router.post("/uploadfile")
def artwork_upload(uploadfile: UploadFile = File(...)):
    path = f"images/{uploadfile.filename}"  # stores uploaded files in a static folder named images
    with open(path, "w+b") as image:
        shutil.copyfileobj(uploadfile.file, image)
    return {"filename": path, "type": uploadfile.content_type}


# to retrieve and download an image via an endpoint
@router.get("/download/{name}", response_class=FileResponse)
async def get_file(name: str):
    path = f"images/{name}"
    return path
