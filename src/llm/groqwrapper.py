# groqwrapper.py
from typing import Any, Generator, List, Dict
import os
from groq import Groq
from groq.types import ChatCompletion

from src.config.config import Config


class GroqWrapper:
    """A wrapper class for interacting with the Groq API."""

    def __init__(
        self,
        model_name: str = Config.GROQ_MODEL_NAME,
        api_key: str = Config.GROQ_API_KEY
    ) -> None:
        """
        Initialize the GroqWrapper with model settings.

        Args:
            model_name: Name of the Groq model to use
            api_key: Groq API key for authentication
        """
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def _response(self, message: str) -> Generator[ChatCompletion, None, None]:
        """
        Generate a response stream from the Groq API.

        Args:
            message: Input message to process

        Returns:
            Generator yielding ChatCompletion objects
        """
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]

        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0,
            max_tokens=4096,
            stream=True,
            stop=None,
        )

    def get_response(self, query: str) -> str:
        """
        Get a complete response for a given query.

        Args:
            query: Input query string

        Returns:
            Complete response string from the model
        """
        response = self._response(query)
        final_answer = ""
        for chunk in response:
            final_answer += chunk.choices[0].delta.content or ""

        return final_answer