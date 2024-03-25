from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import authentication_route
from models import gallery_model
from routes import authuser_route

from .database import engine

app = FastAPI()

gallery_model.Base.metadata.create_all(bind=engine)


@app.get("/apihealthcheck", tags=["test"])
async def get_api_status():
    return {"This art API is Live!"}


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authuser_route.router)
app.include_router(authentication_route.router)
