import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    def __init__(self):
        required_keys = ["ANTHROPIC_API_KEY", "REDIS_URL", "DATABASE_URL", "CHROMA_PATH", "MODEL"]
        for key in required_keys:
            val = os.getenv(key)
            if val is None:
                raise ValueError(f"CRITICAL: Environment variable '{key}' is missing from .env or environment!")
        
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.CHROMA_PATH = os.getenv("CHROMA_PATH")
        self.MODEL = os.getenv("MODEL")

settings = Settings()
