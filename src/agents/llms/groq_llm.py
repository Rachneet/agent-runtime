import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqLLM:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

    def get_llm(self):

        try:
            self.model = ChatGroq(api_key=self.api_key, model="llama-3.1-8b-instant")
            return self.model
        except Exception as e:
            logger.error(f"Error initializing Groq LLM: {e}")
            return None
