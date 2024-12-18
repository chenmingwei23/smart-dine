from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, restaurants
from .services.database import database

app = FastAPI(title="SmartDine API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(restaurants.router, prefix="/api/v1", tags=["restaurants"])

@app.on_event("startup")
async def startup():
    await database.connect_to_database()

@app.on_event("shutdown")
async def shutdown():
    await database.close_database_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to SmartDine API"} 