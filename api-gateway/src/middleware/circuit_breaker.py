from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from typing import Dict, Tuple
from ..config import get_settings

settings = get_settings()

class CircuitState:
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Service unavailable
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

class CircuitBreaker:
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = asyncio.Lock()

    async def record_failure(self):
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD:
                self.state = CircuitState.OPEN

    async def record_success(self):
        async with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    async def check_state(self) -> str:
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT:
                    self.state = CircuitState.HALF_OPEN
            return self.state

class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def _get_service_from_path(self, path: str) -> str:
        if "auth" in path:
            return "auth-service"
        elif "restaurants" in path:
            return "restaurant-service"
        elif "preferences" in path:
            return "preference-service"
        elif "reviews" in path:
            return "review-service"
        return "unknown"

    def _get_circuit_breaker(self, service: str) -> CircuitBreaker:
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]

    async def dispatch(self, request: Request, call_next):
        service = self._get_service_from_path(request.url.path)
        breaker = self._get_circuit_breaker(service)

        state = await breaker.check_state()
        
        if state == CircuitState.OPEN:
            raise HTTPException(
                status_code=503,
                detail=f"Service {service} is temporarily unavailable"
            )

        try:
            response = await call_next(request)
            
            if state == CircuitState.HALF_OPEN:
                await breaker.record_success()
                
            return response
            
        except Exception as e:
            await breaker.record_failure()
            raise HTTPException(
                status_code=503,
                detail=f"Service {service} is experiencing issues"
            ) 