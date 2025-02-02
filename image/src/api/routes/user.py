from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models.user import User
from services.mongodb_service import MongoDBService
from config.logger import logger

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# Dependency
async def get_mongodb_service():
    mongo_service = MongoDBService()
    try:
        await mongo_service.connect()
        yield mongo_service
    finally:
        await mongo_service.close()


@router.get("", response_model=List[User])
async def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> List[User]:
    """
    Get all users with pagination
    """
    try:
        users = await mongo_service.get_all_users(skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.get("/{email}", response_model=User)
async def get_user(
    email: str, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> User:
    """
    Get a user by email
    """
    try:
        user = await mongo_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user")


@router.post("", response_model=User)
async def create_user(
    user: User, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> User:
    """
    Create a new user
    """
    try:
        # Check if user already exists
        existing_user = await mongo_service.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

        created_user = await mongo_service.create_user(user)
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.patch("/{email}", response_model=User)
async def update_user(
    email: str,
    user_update: dict,
    mongo_service: MongoDBService = Depends(get_mongodb_service),
) -> User:
    """
    Update a user partially. Send only the fields you want to update.
    Example: {"phone_number": "new_number", "bio": "new bio"}
    """
    try:
        # First check if user exists
        existing_user = await mongo_service.get_user_by_email(email)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        updated_user = await mongo_service.update_user(email, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user")
