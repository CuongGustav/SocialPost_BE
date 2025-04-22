from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.utils.database import engine
from src.models.base import Base
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.post import router as post_router

app = FastAPI(title="SocialPost API")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router)
app.include_router(post_router)

@app.get("/")
async def root():
    return {"message": "Welcome to SocialPost API"}
