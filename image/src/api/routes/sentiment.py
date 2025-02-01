from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import uuid
from config.logger import logger

from models.sentiment import JournalEntry, JournalAnalysisResponse, EmotionAnalysis
from services.huggingface_service import HuggingFaceService

router = APIRouter(prefix="/api/v1/journal", tags=["Journal"])


# Dependency
async def get_huggingface_service():
    try:
        return HuggingFaceService()
    except Exception as e:
        logger.error(
            f"Failed to initialize HuggingFaceService: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to initialize sentiment analysis service"
        )


@router.post("/analyze", response_model=JournalAnalysisResponse)
async def analyze_journal_entry(
    entry: JournalEntry,
    hf_service: HuggingFaceService = Depends(get_huggingface_service),
) -> JournalAnalysisResponse:
    """
    Analyze emotions in a journal entry
    """
    try:
        logger.info(f"Processing journal entry for user: {entry.user_id}")
        logger.debug(f"Journal entry length: {len(entry.content)}")

        # Get emotion analysis from HuggingFace
        analysis_result = await hf_service.analyze_emotions(entry.content)

        # Create emotion analysis response
        emotion_analysis = EmotionAnalysis(
            emotions=analysis_result["emotions"],
            dominant_emotion=analysis_result["dominant_emotion"],
            timestamp=analysis_result["timestamp"],
            entry_id=str(uuid.uuid4()),
        )

        logger.info(
            f"Successfully analyzed journal entry. Dominant emotion: {emotion_analysis.dominant_emotion}"
        )

        return JournalAnalysisResponse(status="success", analysis=emotion_analysis)

    except Exception as e:
        error_msg = f"Error processing journal entry: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
