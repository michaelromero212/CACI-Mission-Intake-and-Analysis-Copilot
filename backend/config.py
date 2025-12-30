"""
Configuration management using pydantic-settings.
All configuration is loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - defaults to SQLite for easy local development
    # Set DATABASE_URL to PostgreSQL connection string for production
    database_url: str = "sqlite+aiosqlite:///./mission_copilot.db"
    
    # Hugging Face
    huggingface_api_key: str = ""
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Application
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    
    # Cost Transparency (Hugging Face free tier = $0)
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
