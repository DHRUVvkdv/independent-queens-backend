from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import uuid
from datetime import datetime

from config.logger import logger
from models.offer import OfferCreate, OfferResponse, OfferUpdate
from services.mongodb_service import get_mongodb_service

router = APIRouter(prefix="/api/v1/offers", tags=["Offers"])


@router.post("", response_model=OfferResponse)
async def create_offer(
    offer: OfferCreate,
    db_service=Depends(get_mongodb_service),
) -> OfferResponse:
    """Create a new offer"""
    try:
        offer_dict = offer.dict()
        offer_dict["id"] = str(uuid.uuid4())
        offer_dict["created_at"] = datetime.utcnow()

        result = await db_service.offers_collection.insert_one(offer_dict)
        if result.inserted_id:
            logger.info(f"Created offer with ID: {offer_dict['id']}")
            return OfferResponse(**offer_dict)
        raise HTTPException(status_code=500, detail="Failed to create offer")
    except Exception as e:
        error_msg = f"Error creating offer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("", response_model=List[OfferResponse])
async def get_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    skill: str = None,
    db_service=Depends(get_mongodb_service),
) -> List[OfferResponse]:
    """Get all offers with optional filtering"""
    try:
        query = {}
        if skill:
            query["skill"] = skill

        cursor = db_service.offers_collection.find(query).skip(skip).limit(limit)
        offers = await cursor.to_list(length=limit)
        return [OfferResponse(**offer) for offer in offers]
    except Exception as e:
        error_msg = f"Error fetching offers: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: str,
    db_service=Depends(get_mongodb_service),
) -> OfferResponse:
    """Get a specific offer by ID"""
    try:
        offer = await db_service.offers_collection.find_one({"id": offer_id})
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return OfferResponse(**offer)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error fetching offer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.put("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: str,
    offer_update: OfferUpdate,
    db_service=Depends(get_mongodb_service),
) -> OfferResponse:
    """Update an offer"""
    try:
        # Get only the set fields
        update_data = offer_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_data["updated_at"] = datetime.utcnow()

        result = await db_service.offers_collection.update_one(
            {"id": offer_id}, {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Offer not found")

        updated_offer = await db_service.offers_collection.find_one({"id": offer_id})
        return OfferResponse(**updated_offer)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error updating offer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.delete("/{offer_id}")
async def delete_offer(
    offer_id: str,
    db_service=Depends(get_mongodb_service),
):
    """Delete an offer"""
    try:
        result = await db_service.offers_collection.delete_one({"id": offer_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Offer not found")
        logger.info(f"Deleted offer with ID: {offer_id}")
        return {"message": "Offer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error deleting offer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
