import os
from groq import Groq
from src.config import Config


class GroqWrapper:
    def __init__(self, model_name: str = Config.GROQ_MODEL_NAME,  api_key: str = Config.GROQ_API_KEY) -> None:
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
    

    def _response(self, message):

        messages=[
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


    def get_response(self, query: str ) -> str:

        response = self._response(query)
        final_answer = ""
        for chunk in response:
            final_answer += chunk.choices[0].delta.content or ""

        return final_answer



