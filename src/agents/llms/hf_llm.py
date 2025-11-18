import logging
from typing import Optional

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from src.config import settings

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HfLLM:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        

    def _get_api_token(self) -> Optional[str]:
        secret = settings.HUGGINGFACE_API_KEY
        if secret:
            try:
                return secret.get_secret_value()
            except Exception:
                # In case a SecretStr-like object isn't present or accessible
                return str(secret)
        return None
        
    def get_llm(self):

        try:
            model = self.model_name or settings.MODEL_ID
            token = self._get_api_token()

            model_endpoint = HuggingFaceEndpoint(
                model=model,
                huggingfacehub_api_token=token,
            )
            llm = ChatHuggingFace(
                llm=model_endpoint,
            )
            return llm
        except Exception as e:
            logger.error(f"Error initializing Hugging Face LLM: {e}")
            return None
        

if __name__ == "__main__":
    # test the HfLLM class
    hf_llm_instance = HfLLM()
    llm = hf_llm_instance.get_llm()
    if llm:
        response = llm.invoke([{"role": "user", "content": "Hello, how are you?"}])
        print("LLM Response:", response)
    else:
        print("Failed to initialize the Hugging Face LLM.")