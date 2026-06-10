import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://railmind:railmind@localhost:5432/railmind")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_store")
    MODEL: str = os.getenv("MODEL", "claude-3-5-sonnet-20241022")

settings = Settings()
