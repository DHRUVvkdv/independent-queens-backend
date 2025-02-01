from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Women Empowerment Platform API",
    description="API for women's health tracking and community platform",
    version="1.0.0",
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
