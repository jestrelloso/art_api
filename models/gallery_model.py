from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from sqlalchemy import TIMESTAMP, CheckConstraint, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import URLType

from app.database import Base


# DATABASE model for Authenticated or Registration of user // For authentication fields
class Artist(Base):
    __tablename__ = "artist"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    artwork = relationship("Artwork", back_populates="artist", cascade="all, delete")
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())

    __table_args__ = (
        CheckConstraint("length(username) > 0", name="non_empty_username"),
        CheckConstraint("length(password) > 0", name="non_empty_password"),
    )


# DATABASE model for artworks
class Artwork(Base):
    __tablename__ = "artwork"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(URLType, nullable=False)
    artist_id = Column(GUID, ForeignKey("artist.id", ondelete="CASCADE"))
    artist = relationship("Artist", back_populates="artwork")
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="non_empty_name"),
        CheckConstraint("length(description) > 0", name="non_empty_description"),
    )
