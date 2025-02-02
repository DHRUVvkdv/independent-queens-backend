from fastapi import APIRouter, Depends, HTTPException, Body
from services.mongodb_service import MongoDBService
from services.menstrual_health_service import MenstrualHealthService
from services.menstrual_recommendations_service import MenstrualRecommendationsService
from services.openai_service import OpenAIService
from models.menstrual_health import PhaseResponse
from models.menstrual_recommendations import MenstrualRecommendations
from api.routes.user import get_mongodb_service
from config.logger import logger
from models.user import Event
from typing import List
from models.suggested_event import SuggestedEvent
import uuid
from services.event_suggestion_service import EventSuggestionService
from datetime import datetime

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


@router.get("/{email}/suggested-events", response_model=List[SuggestedEvent])
async def get_event_suggestions(
    email: str,
    mongo_service: MongoDBService = Depends(get_mongodb_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> List[SuggestedEvent]:
    """
    Get personalized event suggestions based on user's phase, schedule, and preferences
    """
    try:
        # Get user data
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create suggestion service
        suggestion_service = EventSuggestionService(openai_service)

        # Generate suggestions
        suggested_events = await suggestion_service.get_suggested_events(user)
        return suggested_events

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating event suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate event suggestions"
        )


@router.post("/{email}/accept-event", response_model=Event)
async def accept_suggested_event(
    email: str,
    event: SuggestedEvent = Body(...),
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> Event:
    """
    Accept a suggested event and add it to the user's schedule
    """
    try:
        # Get user data
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create new event
        new_event = Event(
            id=str(uuid.uuid4()),  # Generate new ID for actual event
            title=event.title,
            start=event.start,
            end=event.end,
            color=event.color,
        )

        # Get existing events and add new one
        current_events = user.events if user.events else []
        current_events.append(new_event)

        # Update user's events
        updated_user = await mongo_service.update_user(
            email, {"events": current_events, "updated_at": datetime.utcnow()}
        )

        if not updated_user:
            raise HTTPException(
                status_code=500, detail="Failed to update user's schedule"
            )

        return new_event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting suggested event: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to accept suggested event")
