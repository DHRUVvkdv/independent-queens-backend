import os
from typing import Dict
from datetime import datetime
from fastapi import HTTPException
from config.logger import logger

# Import from langchain packages
from langchain_core.messages import HumanMessage

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    logger.error(
        "langchain_openai not found. Make sure to install: pip install langchain-openai"
    )
    raise ImportError("Please install langchain-openai: pip install langchain-openai")


class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        try:
            self.chat_model = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-3.5-turbo",
                api_key=self.api_key,
                streaming=False,
            )
            logger.info("OpenAIService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI service: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to initialize OpenAI service: {str(e)}")

    async def test_completion(self, prompt: str) -> Dict:
        """
        Test OpenAI integration with a simple completion request

        Args:
            prompt: The prompt to send to OpenAI

        Returns:
            Dict containing the response and timestamp
        """
        try:
            logger.debug(f"Sending request to OpenAI with prompt length: {len(prompt)}")

            messages = [HumanMessage(content=prompt)]
            response = await self.chat_model.ainvoke(messages)

            result = {
                "response": response.content,
                "timestamp": datetime.utcnow(),
                "model": self.chat_model.model_name,
            }

            logger.info("Successfully received OpenAI response")
            return result

        except Exception as e:
            error_msg = f"Error getting completion from OpenAI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)
