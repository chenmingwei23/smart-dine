from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from redis import Redis
from typing import Optional
import httpx
import time

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    BACKEND_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"

app = FastAPI(title="SmartDine API Gateway")
settings = Settings()

# Redis client for rate limiting and caching
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current request count
    requests = redis.get(key)
    if requests is None:
        redis.setex(key, settings.RATE_LIMIT_WINDOW, 1)
    elif int(requests) >= settings.RATE_LIMIT_REQUESTS:
        return Response(
            status_code=429,
            content="Rate limit exceeded. Please try again later."
        )
    else:
        redis.incr(key)
    
    response = await call_next(request)
    return response

# Caching middleware
@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    if request.method != "GET":
        return await call_next(request)
    
    cache_key = f"cache:{request.url.path}:{request.query_params}"
    cached_response = redis.get(cache_key)
    
    if cached_response:
        return Response(
            content=cached_response,
            media_type="application/json"
        )
    
    response = await call_next(request)
    if response.status_code == 200:
        redis.setex(cache_key, 300, response.body)  # Cache for 5 minutes
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Proxy routes to backend services
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_backend(request: Request, path: str):
    client = httpx.AsyncClient()
    url = f"{settings.BACKEND_URL}/{path}"
    
    # Forward the request
    response = await client.request(
        method=request.method,
        url=url,
        headers=request.headers,
        params=request.query_params,
        content=await request.body()
    )
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 