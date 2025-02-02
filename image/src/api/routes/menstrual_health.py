from fastapi import APIRouter, Depends, HTTPException
from services.mongodb_service import MongoDBService
from services.menstrual_health_service import MenstrualHealthService
from models.menstrual_health import PhaseResponse
from api.routes.user import get_mongodb_service
from config.logger import logger

router = APIRouter(prefix="/api/v1/menstrual-health", tags=["Menstrual Health"])


@router.get("/{email}/phase", response_model=PhaseResponse)
async def get_menstrual_phase(
    email: str, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> PhaseResponse:
    """
    Get the current menstrual phase for a user based on their QA pairs.
    Returns phase information if data is available, otherwise indicates missing data.
    """
    try:
        # Get user data
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate phase using the service
        return MenstrualHealthService.calculate_phase(user.qa_pairs)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating menstrual phase: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to calculate menstrual phase"
        )
