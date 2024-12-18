from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import auth, restaurants
from .services.database import database
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect_to_database()
    yield
    # Shutdown
    await database.close_database_connection()

app = FastAPI(title=f"SmartDine {os.getenv('SERVICE_NAME', 'Service')}", lifespan=lifespan)

# Configure CORS - this will be handled by API Gateway in production
if os.getenv("ENVIRONMENT") == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers based on service type
service_name = os.getenv("SERVICE_NAME", "")

if service_name == "auth-service":
    app.include_router(auth.router, tags=["auth"])
elif service_name == "restaurant-service":
    app.include_router(restaurants.router, tags=["restaurants"])
# Add other service routers as needed

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": os.getenv("SERVICE_NAME", "unknown")
    }

@app.get("/")
async def root():
    return {"message": "Welcome to SmartDine API"} 