import json
from typing import Dict, Optional
from models.user import User, QAPair
from models.menstrual_recommendations import MenstrualRecommendations
from services.menstrual_health_service import MenstrualHealthService
from services.openai_service import OpenAIService
from config.logger import logger


class MenstrualRecommendationsService:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.health_service = MenstrualHealthService()

    def _create_prompt(self, user: User, phase: str, has_confidence: bool) -> str:
        """Create a detailed prompt for OpenAI based on user data"""

        # Get mood and confidence from QA pairs
        mood = "neutral"
        for qa in user.qa_pairs:
            if qa.question == "How would you describe your mood recently?":
                mood = qa.answer

        # Create the base prompt
        prompt = f"""As a menstrual health expert, provide personalized recommendations for a {user.age}-year-old person in their {phase} phase who is feeling {mood}. 
Their confidence in menstrual health knowledge is {'high' if has_confidence else 'low'}.

Return the response in the following JSON format:
{{
    "diet_recommendations": [
        // 6 specific diet recommendations including:
        // - General nutrition
        // - Specific foods to include
        // - Foods to avoid
        // - Meal timing
        // - Hydration
        // - Nutrients/supplements
    ],
    "exercise_recommendations": [
        // 6 specific, phase-appropriate exercise recommendations
        // Consider age and energy levels
    ],
    "symptoms_to_watch": [
        // 6 phase-specific symptoms to be aware of
        // Include both common and less common signs
    ],
    "affirmation": "One phase and mood appropriate affirmation"
}}

Make recommendations specific, actionable, and appropriate for their age and knowledge level.
If confidence is low, include brief explanations.
Ensure each point is clear and self-contained.
Use natural, encouraging language."""

        return prompt

    async def get_recommendations(self, user: User) -> MenstrualRecommendations:
        """Generate personalized recommendations for the user"""
        try:
            # Calculate current phase
            phase_response = self.health_service.calculate_phase(user.qa_pairs)
            if not phase_response.has_data:
                raise ValueError(
                    "Insufficient menstrual data to generate recommendations"
                )

            # Check confidence level
            has_confidence = False
            for qa in user.qa_pairs:
                if (
                    qa.question
                    == "Do you feel confident about your knowledge about your menstrual health"
                ):
                    has_confidence = qa.answer.lower() == "yes"
                    break

            # Generate recommendations using OpenAI
            prompt = self._create_prompt(user, phase_response.phase, has_confidence)
            response = await self.openai_service.test_completion(prompt)

            # Parse OpenAI response
            recommendations_data = json.loads(response["response"])

            # Create recommendation object
            return MenstrualRecommendations(
                phase=phase_response.phase,
                diet_recommendations=recommendations_data["diet_recommendations"],
                exercise_recommendations=recommendations_data[
                    "exercise_recommendations"
                ],
                symptoms_to_watch=recommendations_data["symptoms_to_watch"],
                affirmation=recommendations_data["affirmation"],
            )

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}", exc_info=True)
            raise ValueError("Failed to parse recommendations")
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            raise
