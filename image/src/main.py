from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from datetime import datetime
import os
from dotenv import load_dotenv

# Import routes
from api.routes import (
    sentiment,
    user,
    offer,
    journal,
    auth,
    openai_test,
    menstrual_health,
    canvas,
)

# Load environment variables
load_dotenv()

# Security settings
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("NEXT_API_KEY")

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

# Include routers
app.include_router(sentiment.router, dependencies=[Depends(get_api_key)])
app.include_router(user.router, dependencies=[Depends(get_api_key)])
app.include_router(offer.router, dependencies=[Depends(get_api_key)])
app.include_router(journal.router, dependencies=[Depends(get_api_key)])
app.include_router(auth.router, dependencies=[Depends(get_api_key)])
app.include_router(openai_test.router, dependencies=[Depends(get_api_key)])
app.include_router(menstrual_health.router, dependencies=[Depends(get_api_key)])
app.include_router(canvas.router, dependencies=[Depends(get_api_key)])


# AWS Lambda handler
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
