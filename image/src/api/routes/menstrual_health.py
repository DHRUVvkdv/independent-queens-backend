from fastapi import APIRouter, Depends, HTTPException
from services.mongodb_service import MongoDBService
from services.menstrual_health_service import MenstrualHealthService
from services.menstrual_recommendations_service import MenstrualRecommendationsService
from services.openai_service import OpenAIService
from models.menstrual_health import PhaseResponse
from models.menstrual_recommendations import MenstrualRecommendations
from api.routes.user import get_mongodb_service
from config.logger import logger

router = APIRouter(prefix="/api/v1/menstrual-health", tags=["Menstrual Health"])


# Dependency for OpenAI service
async def get_openai_service():
    return OpenAIService()


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


@router.get("/{email}/recommendations", response_model=MenstrualRecommendations)
async def get_personalized_recommendations(
    email: str,
    mongo_service: MongoDBService = Depends(get_mongodb_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> MenstrualRecommendations:
    """
    Get personalized recommendations based on user's phase, age, and other factors
    """
    try:
        # Get user data
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create recommendation service
        recommendation_service = MenstrualRecommendationsService(openai_service)

        # Generate recommendations
        recommendations = await recommendation_service.get_recommendations(user)
        return recommendations

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate recommendations"
        )
