import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from models import gallery_model
from schemas import gallery_schema

router = APIRouter(prefix="/api/artwork", tags=["Artwork"])


# Route for creating an artwork
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_artwork(
    request: gallery_schema.ArtworkSchema,
    db: Session = Depends(get_db),
):

    try:
        # path = f"images/{uploadfile.filename}"  # stores uploaded files in a static folder named images
        # with open(path, "w+b") as buffer:
        #     shutil.copyfileobj(uploadfile.file, buffer)

        new_artwork = gallery_model.Artwork(
            name=request.name,
            description=request.description,
            image=request.image,
            user_id=request.user_id,
        )

        db.add(new_artwork)

        db.commit()

        db.refresh(new_artwork)

        return {"New Artwork": new_artwork}
    except Exception as e:
        # If an error occurs, raise an HTTPException with status 400 and the error message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# to upload files that has a .jpeg, .png file types
@router.post("/uploadfile")
def artwork_upload(uploadfile: UploadFile = File(...)):
    path = f"images/{uploadfile.filename}"  # stores uploaded files in a static folder named images
    with open(path, "w+b") as buffer:
        shutil.copyfileobj(uploadfile.file, buffer)
    return {"filename": path, "type": uploadfile.content_type}


# to retrieve and download an image via an endpoint
@router.get("/download/{name}", response_class=FileResponse)
async def get_file(name: str):
    path = f"images/{name}"
    return path
