
from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    MODEL_NAME = "llama3-8b-8192"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.1-8b-instant"

