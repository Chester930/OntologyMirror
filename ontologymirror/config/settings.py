import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Global settings for OntologyMirror.
    Uses pydantic-settings to read from environment variables or .env file.
    """
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    REPOS_DIR: Path = DATA_DIR / "raw_repos"
    
    # LLM Settings
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # Tool Settings
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra env vars
    )

# Create global instance
# Ensure directories exist
os.makedirs(Settings().DATA_DIR, exist_ok=True)
os.makedirs(Settings().REPOS_DIR, exist_ok=True)

settings = Settings()
