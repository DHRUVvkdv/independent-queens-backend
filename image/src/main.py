from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security settings
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY")  # Set this in .env

# Security dependency
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key"""
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")


# Initialize FastAPI app
app = FastAPI(
    title="Women Empowerment Platform API",
    description="API for women's health tracking and community platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Lambda handler
handler = Mangum(app)


# Models
class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    environment: str


# Routes
@app.get(
    "/api/v1/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health check endpoint",
    response_description="Basic health check response with system status",
    dependencies=[Depends(get_api_key)],  # Add this line to protect the endpoint
)
async def health_check() -> HealthCheckResponse:
    """
    Performs a health check of the system.

    Returns:
        HealthCheckResponse: Object containing system health information
    """
    try:
        return HealthCheckResponse(
            status="Dhruv is healthy!",
            version="1.0.0",
            timestamp=datetime.utcnow(),
            environment=os.getenv("ENVIRONMENT", "development"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
