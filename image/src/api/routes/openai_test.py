from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from services.openai_service import OpenAIService
from config.logger import logger

router = APIRouter(prefix="/api/v1/openai", tags=["OpenAI"])


class PromptRequest(BaseModel):
    prompt: str


class OpenAIResponse(BaseModel):
    response: str
    timestamp: datetime  # Changed from str to datetime
    model: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Dependency
async def get_openai_service():
    try:
        service = OpenAIService()
        return service
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to initialize OpenAI service"
        )


@router.post("/test", response_model=OpenAIResponse)
async def test_openai(
    request: PromptRequest, openai_service: OpenAIService = Depends(get_openai_service)
) -> OpenAIResponse:
    """
    Test OpenAI integration with a simple completion request
    """
    try:
        result = await openai_service.test_completion(request.prompt)
        return OpenAIResponse(**result)
    except Exception as e:
        logger.error(f"Error in OpenAI test endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process OpenAI request")
