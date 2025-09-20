from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import sys
import os
import time
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.coding_agent import CodingAgent
from monitoring.middleware import LoggingMiddleware, MetricsMiddleware
from monitoring.logger_config import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Computer Use Coding Assistant API",
    version="1.0.0",
    description="AI-powered coding assistant with computer control capabilities"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(MetricsMiddleware)

# Request/Response models
class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    status: str
    response: Optional[str] = None
    error: Optional[str] = None
    task_summary: Optional[str] = None
    execution_time: Optional[float] = None
    request_id: Optional[str] = None

# Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Computer Use Coding Assistant API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "execute": "/execute",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest, req: Request):
    """Execute a coding task"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Executing task: {request.task[:100]}...", extra={"request_id": request_id})
    
    try:
        agent = CodingAgent()
        result = await agent.execute_task(request.task, request.context)
        
        execution_time = time.time() - start_time
        
        return TaskResponse(
            **result,
            execution_time=execution_time,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "computer-use-coding-assistant",
        "timestamp": time.time()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest
    from fastapi.responses import Response
    
    return Response(content=generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
