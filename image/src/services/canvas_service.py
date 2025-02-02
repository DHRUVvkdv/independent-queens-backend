# services/canvas_service.py
from datetime import datetime, timedelta
import aiohttp
import asyncio
from models.user import Assignment
from typing import List
from config.logger import logger


class CanvasService:
    def __init__(self, api_token: str):
        self.base_url = "https://canvas.instructure.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    async def get_assignments(self) -> List[Assignment]:
        """Fetch assignments for the next 7 days"""
        try:
            # First, get all active courses with more details
            courses = await self.get_courses()
            if not courses:
                logger.error("No courses found")
                return []

            assignments = []
            current_date = datetime.utcnow().replace(tzinfo=None)
            end_date = current_date + timedelta(days=7)

            logger.info(f"Fetching assignments between {current_date} and {end_date}")

            async with aiohttp.ClientSession(headers=self.headers) as session:
                assignment_tasks = []
                for course in courses:
                    course_id = course["id"]
                    url = f"{self.base_url}/courses/{course_id}/assignments"
                    params = {
                        "include[]": ["submission"],
                        "bucket": "upcoming",
                        "per_page": 50,
                    }
                    assignment_tasks.append(
                        self.fetch_course_assignments(
                            session, url, str(course_id), params
                        )
                    )

                course_assignments_list = await asyncio.gather(
                    *assignment_tasks, return_exceptions=True
                )

                for course_assignments in course_assignments_list:
                    if isinstance(course_assignments, Exception):
                        logger.error(
                            f"Error fetching assignments: {str(course_assignments)}"
                        )
                        continue

                    for assignment in course_assignments:
                        try:
                            if not assignment.get("due_at"):
                                continue

                            due_date = datetime.fromisoformat(
                                assignment["due_at"].replace("Z", "+00:00")
                            ).replace(tzinfo=None)

                            # Debug log for assignment dates
                            logger.info(
                                f"Assignment: {assignment.get('name')} - Due: {due_date}"
                            )
                            logger.info(f"Current: {current_date} - End: {end_date}")

                            if current_date <= due_date <= end_date:
                                logger.info(
                                    f"Found valid assignment: {assignment.get('name')}"
                                )
                                assignments.append(
                                    Assignment(
                                        name=assignment.get(
                                            "name", "Unnamed Assignment"
                                        ),
                                        date_due=due_date.strftime("%Y-%m-%d"),
                                        time_due=due_date.strftime("%H:%M"),
                                        canvas_link=assignment.get("html_url", ""),
                                    )
                                )
                        except Exception as e:
                            logger.error(f"Error processing assignment: {str(e)}")
                            continue

            logger.info(f"Total assignments found for next 7 days: {len(assignments)}")
            return assignments

        except Exception as e:
            logger.error(f"Error fetching Canvas assignments: {str(e)}", exc_info=True)
            return []

    async def fetch_course_assignments(self, session, url, course_id, params):
        """Fetch assignments for a single course"""
        try:
            async with session.get(url, params=params) as response:
                # Log raw response for debugging
                response_text = await response.text()
                logger.info(
                    f"Raw response for course {course_id}: {response_text[:200]}..."
                )  # Log first 200 chars

                if response.status == 403:
                    logger.info(f"No access to assignments for course {course_id}")
                    return []

                if response.status != 200:
                    logger.error(f"Error getting assignments: Status {response.status}")
                    logger.error(f"Response body: {response_text}")
                    return []

                assignments = await response.json()
                logger.info(
                    f"Fetched {len(assignments)} assignments for course: {course_id}"
                )
                return assignments

        except Exception as e:
            logger.error(f"Error fetching assignments for course {course_id}: {str(e)}")
            return []

    async def get_courses(self):
        """Get active courses for the user"""
        try:
            url = f"{self.base_url}/courses"
            params = {
                "enrollment_state": "active",
                "include[]": ["term"],
                "per_page": 100,
                "state[]": ["available"],
            }

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Canvas API error: Status {response.status}")
                        logger.error(f"Response: {await response.text()}")
                        return []

                    courses = await response.json()
                    if courses:
                        # Log full structure of first course for debugging
                        logger.info(f"Complete course data: {courses[0]}")

                    logger.info(f"Found {len(courses)} courses")
                    return courses

        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}", exc_info=True)
            return []
