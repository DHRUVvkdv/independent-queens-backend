# api/routes/canvas.py
from fastapi import APIRouter, Depends, HTTPException
from services.canvas_service import CanvasService
from services.mongodb_service import MongoDBService
from typing import List
from models.user import Assignment
from config.logger import logger

router = APIRouter(prefix="/api/v1/canvas", tags=["Canvas"])


# Dependency
async def get_mongodb_service():
    mongo_service = MongoDBService()
    try:
        await mongo_service.connect()
        yield mongo_service
    finally:
        await mongo_service.close()


@router.get("/assignments", response_model=List[Assignment])
async def get_canvas_assignments(
    email: str, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> List[Assignment]:
    """
    Get Canvas assignments for the current week for a specific user
    """
    try:
        # Get user and their Canvas token
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.canvas_token:
            raise HTTPException(status_code=400, detail="Canvas token not set for user")

        # Initialize Canvas service with user's token
        canvas_service = CanvasService(user.canvas_token)

        # Fetch assignments
        assignments = await canvas_service.get_assignments()
        return assignments

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Canvas assignments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch Canvas assignments"
        )
