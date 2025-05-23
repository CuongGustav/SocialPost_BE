from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.staticfiles import StaticFiles
from src.utils.database import engine
from src.models.base import Base
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.post import router as post_router
from src.api.endpoints.user import router as user_router
from src.api.endpoints.interaction import router as interaction_router
from src.api.endpoints.comment import router as comment_router
from src.api.endpoints.violation import router as violation_router

app = FastAPI(title="SocialPost API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(post_router)
app.include_router(user_router)
app.include_router(interaction_router)
app.include_router(comment_router)
app.include_router(violation_router)


@app.get("/")
async def root():
    return {"message": "Welcome to SocialPost API"}
