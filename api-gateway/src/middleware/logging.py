from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from typing import Dict, Any
from ..config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("api_gateway")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Prepare request logging info
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Log request
        logger.info(f"Incoming request: {json.dumps(request_info)}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            self._log_response(request_info, response.status_code, duration)
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            
            # Log error
            self._log_error(request_info, e, duration)
            raise

    def _log_response(self, request_info: Dict[str, Any], status_code: int, duration: float):
        log_data = {
            **request_info,
            "status_code": status_code,
            "duration": f"{duration:.3f}s"
        }
        if 200 <= status_code < 400:
            logger.info(f"Request completed: {json.dumps(log_data)}")
        else:
            logger.warning(f"Request failed: {json.dumps(log_data)}")

    def _log_error(self, request_info: Dict[str, Any], error: Exception, duration: float):
        log_data = {
            **request_info,
            "error": str(error),
            "duration": f"{duration:.3f}s"
        }
        logger.error(f"Request error: {json.dumps(log_data)}") 