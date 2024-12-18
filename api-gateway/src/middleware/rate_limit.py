from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import time
from ..config import get_settings

settings = get_settings()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP or user ID if authenticated)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        return await call_next(request)

    def _get_client_id(self, request: Request) -> str:
        # Use user ID if authenticated, otherwise use IP
        if hasattr(request.state, 'user'):
            return f"user:{request.state.user.get('sub')}"
        return f"ip:{request.client.host}"

    def _check_rate_limit(self, client_id: str) -> bool:
        pipe = self.redis.pipeline()
        now = time.time()
        key = f"rate_limit:{client_id}"
        
        # Clean old requests
        pipe.zremrangebyscore(
            key,
            0,
            now - settings.RATE_LIMIT_WINDOW
        )
        
        # Count requests in window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiry
        pipe.expire(key, settings.RATE_LIMIT_WINDOW)
        
        # Execute pipeline
        _, request_count, *_ = pipe.execute()
        
        return request_count < settings.RATE_LIMIT_MAX_REQUESTS 