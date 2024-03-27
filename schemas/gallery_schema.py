from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


# ARTWORK
class Artwork(BaseModel):
    id: UUID
    name: str
    description: str
    image_url: str

    class Config:
        orm_mode = True


# ARTIST
class Artist(BaseModel):
    id: UUID
    username: str

    class Config:
        orm_mode = True


# ARTWORK Create schema
# class ArtworkSchema(BaseModel):
#     name: str
#     description: str
#     image: str
#     user_id: str
#     createdAt: datetime | None = None
#     updatedAt: datetime | None = None


# ARTIST Create schema
class ArtistSchema(BaseModel):
    username: str
    password: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


# ARTIST Update schema
class ArtistSchemaUpdate(BaseModel):
    username: str
    password: str
    updatedAt: datetime | None = None


# ARTIST Display schema
class ArtistDisplay(BaseModel):
    id: UUID
    username: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    artwork: List[Artwork] = []

    class Config:
        orm_mode = True


# ARTWORK display schema
class ArtworkDisplay(BaseModel):
    id: UUID
    name: str
    description: str
    image_url: str
    artist: Artist

    class Config:
        orm_mode = True
