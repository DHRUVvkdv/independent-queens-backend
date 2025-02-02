from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from models.journal import Journal, EmotionAnalysis
from services.mongodb_service import MongoDBService, get_mongodb_service
from config.logger import logger


router = APIRouter(prefix="/api/v1/journals", tags=["Journals"])


@router.get("/user/{email}", response_model=List[Journal])
async def get_user_journals(
    email: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> List[Journal]:
    """
    Get all journals for a specific user with pagination
    """
    try:
        journals = await mongo_service.get_journals_by_email(
            email, skip=skip, limit=limit
        )
        return journals
    except Exception as e:
        logger.error(f"Error fetching journals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch journals")


@router.get("/{journal_id}", response_model=Journal)
async def get_journal(
    journal_id: str, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> Journal:
    """
    Get a specific journal by ID
    """
    try:
        journal = await mongo_service.get_journal_by_id(journal_id)
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return journal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch journal")


@router.post("", response_model=Journal)
async def create_journal(
    journal: Journal, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> Journal:
    """
    Create a new journal entry
    """
    try:
        # Check if user exists
        user = await mongo_service.get_user_by_email(journal.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        created_journal = await mongo_service.create_journal(journal)
        return created_journal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating journal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create journal")


@router.patch("/{journal_id}", response_model=Journal)
async def update_journal(
    journal_id: str,
    journal_update: dict,
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> Journal:
    """
    Update a journal entry partially. Send only the fields you want to update.
    Example: {"title": "New Title", "description": "New description"}
    """
    try:
        # First check if journal exists
        existing_journal = await mongo_service.get_journal_by_id(journal_id)
        if not existing_journal:
            raise HTTPException(status_code=404, detail="Journal not found")

        updated_journal = await mongo_service.update_journal(journal_id, journal_update)
        if not updated_journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return updated_journal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update journal")


@router.delete("/{journal_id}")
async def delete_journal(
    journal_id: str, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> dict:
    """
    Delete a journal entry
    """
    try:
        # First check if journal exists
        existing_journal = await mongo_service.get_journal_by_id(journal_id)
        if not existing_journal:
            raise HTTPException(status_code=404, detail="Journal not found")

        deleted = await mongo_service.delete_journal(journal_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete journal")
        return {"message": "Journal deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete journal")


@router.patch("/{journal_id}/emotion-analysis", response_model=Journal)
async def update_emotion_analysis(
    journal_id: str,
    emotion_analysis: EmotionAnalysis,
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> Journal:
    """
    Update emotion analysis for a journal entry
    """
    try:
        # First check if journal exists
        existing_journal = await mongo_service.get_journal_by_id(journal_id)
        if not existing_journal:
            raise HTTPException(status_code=404, detail="Journal not found")

        updated_journal = await mongo_service.update_journal_emotion_analysis(
            journal_id, emotion_analysis
        )
        if not updated_journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return updated_journal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emotion analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update emotion analysis")
