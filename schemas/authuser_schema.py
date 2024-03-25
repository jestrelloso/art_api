from datetime import datetime

from pydantic import BaseModel


class AuthSchema(BaseModel):
    username: str
    password: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
