from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from models.user import User
from models.journal import Journal, EmotionAnalysis
from datetime import datetime
import os
from config.logger import logger
from datetime import timedelta


class MongoDBService:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.offers_collection = None
        self.journals_collection = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                os.getenv("MONGODB_URL"), uuidRepresentation="standard"
            )
            self.db = self.client[os.getenv("MONGODB_DB_NAME", "women_empowerment_db")]
            self.users_collection = self.db.users
            self.offers_collection = self.db.offers
            self.journals_collection = self.db.journals

            # Create index on email
            await self.users_collection.create_index("email", unique=True)
            await self.users_collection.create_index("cognito_id", unique=True)

            await self.offers_collection.create_index("email")
            await self.journals_collection.create_index([("email", 1)])
            await self.journals_collection.create_index([("id", 1)], unique=True)

            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        user_dict = await self.users_collection.find_one({"email": email})
        return User(**user_dict) if user_dict else None

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.users_collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [User(**user) for user in users]

    async def create_user(self, user: User) -> User:
        user_dict = user.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()

        await self.users_collection.insert_one(user_dict)
        return user

    async def update_user(self, email: str, user_update: dict) -> Optional[User]:
        user_update["updated_at"] = datetime.utcnow()

        result = await self.users_collection.update_one(
            {"email": email}, {"$set": user_update}
        )

        if result.modified_count:
            return await self.get_user_by_email(email)
        return None

    async def delete_user(self, email: str) -> bool:
        result = await self.users_collection.delete_one({"email": email})
        return result.deleted_count > 0

    async def get_journals_by_email(
        self, email: str, skip: int = 0, limit: int = 100
    ) -> List[Journal]:
        """Get all journals for a specific user with pagination"""
        cursor = self.journals_collection.find({"email": email}).skip(skip).limit(limit)
        journals = await cursor.to_list(length=limit)
        return [Journal(**journal) for journal in journals]

    async def get_journal_by_id(self, journal_id: str) -> Optional[Journal]:
        """Get a specific journal by ID"""
        journal_dict = await self.journals_collection.find_one({"id": journal_id})
        return Journal(**journal_dict) if journal_dict else None

    async def create_journal(self, journal: Journal) -> Journal:
        """Create a new journal entry"""
        journal_dict = journal.dict()
        journal_dict["created_at"] = datetime.utcnow()
        journal_dict["updated_at"] = datetime.utcnow()

        await self.journals_collection.insert_one(journal_dict)
        return journal

    async def update_journal(
        self, journal_id: str, journal_update: dict
    ) -> Optional[Journal]:
        """Update a journal entry"""
        journal_update["updated_at"] = datetime.utcnow()

        result = await self.journals_collection.update_one(
            {"id": journal_id}, {"$set": journal_update}
        )

        if result.modified_count:
            return await self.get_journal_by_id(journal_id)
        return None

    async def delete_journal(self, journal_id: str) -> bool:
        """Delete a journal entry"""
        result = await self.journals_collection.delete_one({"id": journal_id})
        return result.deleted_count > 0

    async def update_journal_emotion_analysis(
        self, journal_id: str, emotion_analysis: EmotionAnalysis
    ) -> Optional[Journal]:
        """Update emotion analysis for a journal entry"""
        result = await self.journals_collection.update_one(
            {"id": journal_id},
            {
                "$set": {
                    "emotion_analysis": emotion_analysis.dict(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.modified_count:
            return await self.get_journal_by_id(journal_id)
        return None

    async def get_journal_insights(self, email: str, days: int = 30) -> dict:
        """Get insights from journals for the past N days"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Format dates for response
            formatted_start = start_date.strftime("%m-%d-%Y")
            formatted_end = end_date.strftime("%m-%d-%Y")

            # MongoDB aggregation pipeline
            pipeline = [
                # Match journals for the user within date range
                {
                    "$match": {
                        "email": email,
                        "$expr": {
                            "$and": [
                                {
                                    "$gte": [
                                        {
                                            "$dateFromString": {
                                                "dateString": "$date",
                                                "format": "%m-%d-%Y",
                                            }
                                        },
                                        start_date,
                                    ]
                                },
                                {
                                    "$lte": [
                                        {
                                            "$dateFromString": {
                                                "dateString": "$date",
                                                "format": "%m-%d-%Y",
                                            }
                                        },
                                        end_date,
                                    ]
                                },
                            ]
                        },
                    }
                },
                # Get total count of entries and emotions data
                {
                    "$facet": {
                        "total_entries": [{"$count": "count"}],
                        "all_emotions": [
                            {
                                "$project": {
                                    "emotions": {
                                        "$objectToArray": "$emotion_analysis.emotions"
                                    }
                                }
                            },
                            {"$unwind": "$emotions"},
                            {
                                "$group": {
                                    "_id": "$emotions.k",
                                    "count": {
                                        "$sum": 1
                                    },  # Count occurrences instead of summing values
                                    "average_score": {
                                        "$avg": "$emotions.v"
                                    },  # Keep track of average score
                                }
                            },
                        ],
                        "dominant_emotions": [
                            {
                                "$group": {
                                    "_id": "$emotion_analysis.dominant_emotion",
                                    "count": {"$sum": 1},
                                }
                            }
                        ],
                    }
                },
            ]

            # Execute aggregation
            result = await self.journals_collection.aggregate(pipeline).next()

            # Process all_emotions results
            all_emotions_dict = {}
            all_emotions_sorted = []
            for emotion in result.get("all_emotions", []):
                if emotion["_id"]:  # Check for valid emotion name
                    count = emotion["count"]
                    avg_score = round(emotion["average_score"], 4)
                    all_emotions_dict[emotion["_id"]] = {
                        "count": count,
                        "average_score": avg_score,
                    }
                    all_emotions_sorted.append(
                        {
                            "emotion": emotion["_id"],
                            "count": count,
                            "average_score": avg_score,
                        }
                    )

            # Sort by count
            all_emotions_sorted.sort(key=lambda x: x["count"], reverse=True)

            # Process dominant_emotions results
            dominant_emotions_dict = {}
            dominant_emotions_sorted = []
            for emotion in result.get("dominant_emotions", []):
                if emotion["_id"]:  # Check for valid emotion name
                    count = emotion["count"]
                    dominant_emotions_dict[emotion["_id"]] = count
                    dominant_emotions_sorted.append(
                        {"emotion": emotion["_id"], "count": count}
                    )

            # Sort by count
            dominant_emotions_sorted.sort(key=lambda x: x["count"], reverse=True)

            # Get total entries count safely
            total_entries = result.get("total_entries", [{"count": 0}])[0].get(
                "count", 0
            )

            # Format final response
            return {
                "metadata": {
                    "date_range": {"start": formatted_start, "end": formatted_end},
                    "total_entries": total_entries,
                },
                "emotions": {
                    "all_emotions": all_emotions_dict,
                    "dominant_emotions": dominant_emotions_dict,
                },
                "sorted_emotions": {
                    "all_emotions": all_emotions_sorted,
                    "dominant_emotions": dominant_emotions_sorted,
                },
            }

        except Exception as e:
            logger.error(f"Error getting journal insights: {str(e)}", exc_info=True)
            raise


async def get_mongodb_service():
    """Dependency function to get MongoDB service instance"""
    db = MongoDBService()
    await db.connect()
    try:
        yield db
    finally:
        await db.close()
