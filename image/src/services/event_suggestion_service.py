import json
from typing import List, Dict
from datetime import datetime, timedelta
import uuid
from models.user import User, Event
from models.suggested_event import SuggestedEvent, EVENT_COLORS
from services.menstrual_health_service import MenstrualHealthService
from services.openai_service import OpenAIService
from config.logger import logger


class EventSuggestionService:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.health_service = MenstrualHealthService()

    def _get_week_range(self) -> tuple[str, str]:
        """Get start and end dates for current week"""
        today = datetime.now()
        week_start = today
        week_end = today + timedelta(days=6)
        return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")

    def _format_events_for_prompt(self, events: List[Event]) -> str:
        """Format existing events for the prompt"""
        events_str = ""
        for event in events:
            events_str += f"- {event.title} from {event.start} to {event.end}\n"
        return events_str

    def _create_prompt(
        self, user: User, phase: str, week_start: str, week_end: str
    ) -> str:
        """Create a detailed prompt for OpenAI based on user data and current schedule"""

        existing_events = self._format_events_for_prompt(user.events)
        interests_str = (
            ", ".join(user.interests)
            if user.interests
            else "no specific interests listed"
        )

        prompt = f"""As an event planning expert, suggest 5-6 personalized events for a {user.age}-year-old {user.profession} 
who is in their {phase} phase of menstrual cycle. Consider their interests: {interests_str}.

Current schedule for reference:
{existing_events}

Generate suggestions for the week of {week_start} to {week_end}.

Return the response in the following JSON format:
{{
    "suggested_events": [
        {{
            "title": "Event title",
            "start": "YYYY-MM-DD HH:MM",
            "end": "YYYY-MM-DD HH:MM",
            "type": "type of activity (wellness/productivity/rest/social/learning)",
            "reason": "Brief explanation of why this event is suggested"
        }}
    ]
}}

Guidelines:
1. Consider phase-appropriate activities (e.g., lighter activities during menstrual phase)
2. Account for age and profession ({user.profession})
3. Incorporate user's interests where relevant
4. Suggest a mix of different activity types
5. Keep time slots reasonable (30-90 minutes)
6. Use 24-hour format for times

Make suggestions specific, actionable, and appropriate for their phase and age."""

        return prompt

    async def get_suggested_events(self, user: User) -> List[SuggestedEvent]:
        """Generate personalized event suggestions for the user"""
        try:
            # Calculate current phase
            phase_response = self.health_service.calculate_phase(user.qa_pairs)
            if not phase_response.has_data:
                raise ValueError("Insufficient menstrual data to generate suggestions")

            # Get week range
            week_start, week_end = self._get_week_range()

            # Generate suggestions using OpenAI
            prompt = self._create_prompt(
                user, phase_response.phase, week_start, week_end
            )
            response = await self.openai_service.test_completion(prompt)

            # Parse OpenAI response
            suggestions_data = json.loads(response["response"])

            # Convert to SuggestedEvent objects
            suggested_events = []
            for event in suggestions_data["suggested_events"]:
                # Generate unique ID for suggestion
                event_id = f"sugg_{str(uuid.uuid4())}"

                # Get color based on event type
                color = EVENT_COLORS.get(
                    event["type"].lower(), "#607D8B"
                )  # Default gray if type not found

                suggested_events.append(
                    SuggestedEvent(
                        id=event_id,
                        title=event["title"],
                        start=event["start"],
                        end=event["end"],
                        color=color,
                        type=event["type"],
                        reason=event["reason"],
                    )
                )

            return suggested_events

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}", exc_info=True)
            raise ValueError("Failed to parse event suggestions")
        except Exception as e:
            logger.error(f"Error generating event suggestions: {str(e)}", exc_info=True)
            raise
