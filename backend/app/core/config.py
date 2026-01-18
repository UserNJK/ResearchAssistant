from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    environment: str = os.getenv("ENVIRONMENT", "development")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    serp_api_key: str = os.getenv("SERP_API_KEY", "")

settings = Settings()