from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from ..config import get_settings

settings = get_settings()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="No authorization header")

        try:
            # Extract and verify JWT token
            token = auth_header.split(" ")[1]
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Add user info to request state
            request.state.user = payload
            
            return await call_next(request)
            
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _is_public_endpoint(self, path: str) -> bool:
        public_paths = [
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/docs",
            "/openapi.json"
        ]
        return any(path.startswith(p) for p in public_paths) 