from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from typing import Callable
import logging

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id}
        )
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code} - {duration:.2f}ms",
                extra={"correlation_id": correlation_id}
            )
            
            response.headers["X-Correlation-ID"] = correlation_id
            return response
            
        except Exception as e:
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={"correlation_id": correlation_id},
                exc_info=True
            )
            raise

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for metrics collection"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
