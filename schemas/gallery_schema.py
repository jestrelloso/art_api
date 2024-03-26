from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


# ARTWORK
class Artwork(BaseModel):
    id: UUID
    name: str
    description: str
    image: str

    class Config:
        orm_mode = True


# USER Create schema
class AuthSchema(BaseModel):
    username: str
    password: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


# USER Update schema
class AuthSchemaUpdate(BaseModel):
    username: str
    password: str
    updatedAt: datetime | None = None


# USER Display schema
class UserDisplay(BaseModel):
    id: UUID
    username: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    artwork: List[Artwork] = []

    class Config:
        orm_mode = True
