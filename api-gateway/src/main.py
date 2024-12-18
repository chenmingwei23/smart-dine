from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.circuit_breaker import CircuitBreakerMiddleware
from .config import Settings
from .routes import auth, restaurants, preferences, reviews
import httpx

app = FastAPI(title="SmartDine API Gateway")
settings = Settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CircuitBreakerMiddleware)

# HTTP client for forwarding requests
http_client = httpx.AsyncClient()

@app.on_event("startup")
async def startup():
    # Initialize services
    pass

@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(restaurants.router, prefix="/api/v1/restaurants", tags=["restaurants"])
app.include_router(preferences.router, prefix="/api/v1/preferences", tags=["preferences"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 