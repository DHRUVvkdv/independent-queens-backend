import os
from typing import Dict, Optional, List
import httpx
from datetime import datetime
import json
import asyncio
from fastapi import HTTPException
from config.logger import logger


class HuggingFaceService:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            logger.error("HUGGINGFACE_API_TOKEN environment variable is not set")
            raise ValueError("HUGGINGFACE_API_TOKEN environment variable is not set")

        self.api_url = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        logger.info("HuggingFaceService initialized successfully")

    def _process_emotions(self, raw_response: List[List[Dict[str, float]]]) -> Dict:
        """
        Process the raw emotion scores from the API response

        Args:
            raw_response: The raw response from the API

        Returns:
            Dict containing processed emotions and dominant emotion
        """
        try:
            # The API returns a list of lists, where each inner list contains emotion predictions
            # We'll take the first set of predictions (raw_response[0])
            predictions = raw_response[0]

            # Convert the list of predictions into a dictionary
            emotions_dict = {}
            for pred in predictions:
                label = pred["label"]
                score = pred["score"]
                emotions_dict[label] = score

            # Find the emotion with the highest score
            dominant_emotion = max(emotions_dict.items(), key=lambda x: x[1])[0]

            return {"emotions": emotions_dict, "dominant_emotion": dominant_emotion}

        except Exception as e:
            logger.error(f"Error processing emotions response: {str(e)}", exc_info=True)
            logger.error(f"Raw response was: {raw_response}")
            raise ValueError(f"Failed to process emotions: {str(e)}")

    async def analyze_emotions(self, text: str, max_retries: int = 3) -> Dict:
        """
        Analyze emotions in the given text using HuggingFace API

        Args:
            text: The text to analyze
            max_retries: Maximum number of retries when model is loading

        Returns:
            Dict containing emotion scores and dominant emotion
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.debug(
                    f"Sending request to HuggingFace API with text length: {len(text)}"
                )
                logger.debug(f"Attempt {retry_count + 1} of {max_retries}")

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.api_url,
                        headers=self.headers,
                        json={"inputs": text},
                        timeout=30.0,
                    )

                    logger.debug(
                        f"HuggingFace API response status: {response.status_code}"
                    )

                    if response.status_code == 200:
                        # Log the raw response for debugging
                        raw_response = response.json()
                        logger.debug(f"Raw API response: {raw_response}")

                        # Process the emotions
                        processed_emotions = self._process_emotions(raw_response)

                        logger.info(
                            f"Successfully analyzed emotions. Dominant emotion: {processed_emotions['dominant_emotion']}"
                        )

                        return {
                            "emotions": processed_emotions["emotions"],
                            "dominant_emotion": processed_emotions["dominant_emotion"],
                            "timestamp": datetime.utcnow(),
                        }

                    elif response.status_code == 503:
                        response_json = response.json()
                        if "estimated_time" in response_json.get("error", ""):
                            # Model is loading, wait and retry
                            wait_time = min(
                                response_json.get("estimated_time", 20), 20
                            )  # Cap at 20 seconds
                            logger.info(
                                f"Model is loading. Waiting {wait_time} seconds before retry."
                            )
                            await asyncio.sleep(wait_time)
                            retry_count += 1
                            continue

                    # If we get here, it's an error we don't want to retry
                    error_msg = f"HuggingFace API error: {response.text}"
                    logger.error(error_msg)
                    logger.error(f"Response headers: {response.headers}")
                    raise HTTPException(
                        status_code=response.status_code, detail=error_msg
                    )

            except httpx.TimeoutException as e:
                error_msg = "Request to HuggingFace API timed out"
                logger.error(f"{error_msg}: {str(e)}")
                raise HTTPException(status_code=504, detail=error_msg)
            except Exception as e:
                error_msg = f"Error analyzing emotions: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise HTTPException(status_code=500, detail=error_msg)

        # If we've exhausted all retries
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Model failed to load after maximum retries.",
        )
