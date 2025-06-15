
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Agent configuration
    MAX_ITERATIONS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.8
    
    # API endpoints
    GOOGLE_AI_ENDPOINT: str = "https://generativelanguage.googleapis.com/v1beta/models"
    # DEPRECATED: We are no longer using this.
    # SPACEX_API_ENDPOINT: str = "https://api.spacexdata.com/v5" 
    
    # NEW: The new, reliable data source for rocket launches.
    ROCKETLAUNCH_LIVE_API_ENDPOINT: str = "https://fdo.rocketlaunch.live/json/launches/next/5"
    
    OPENWEATHER_API_ENDPOINT: str = "https://api.openweathermap.org/data/2.5"
    
    class Config:
        env_file = ".env"

settings = Settings()