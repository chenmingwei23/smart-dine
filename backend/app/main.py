from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .db.base import MongoDB
from .api.v1.endpoints import restaurants, reviews

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await MongoDB.connect_db()
    yield
    # Shutdown
    await MongoDB.close_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    restaurants.router,
    prefix=f"{settings.API_V1_STR}/restaurants",
    tags=["restaurants"]
)

app.include_router(
    reviews.router,
    prefix=f"{settings.API_V1_STR}/reviews",
    tags=["reviews"]
)

@app.get("/health")
async def health_check():
    """Health check endpoint for AWS ALB."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    } 