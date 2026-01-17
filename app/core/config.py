from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sourcing Agent"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/sourcing_agent"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # Google Custom Search
    GOOGLE_API_KEY: str = ""
    GOOGLE_CSE_ID: str = ""
    MAX_GOOGLE_SEARCH_RESULTS: int = 1000  # Max results per search (API limit is 100)

    # Serper API (Google Search alternative)
    SERPER_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
