# Configuration using Pydantic BaseSettings for validation and type safety
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT",
                                       description="Azure OpenAI endpoint URL")
    azure_openai_key: str = Field(..., env="AZURE_OPENAI_KEY",
                                  description="Azure OpenAI API key")
    azure_openai_deployment_name: str = Field(
        ..., env="AZURE_OPENAI_DEPLOYMENT_NAME", description="Azure OpenAI deployment name")
    azure_openai_api_version: str = Field(
        "2024-02-01", env="AZURE_OPENAI_API_VERSION", description="Azure OpenAI API version")

    # Server Configuration
    debug: bool = Field(False, env="DEBUG", description="Enable debug mode")
    host: str = Field("0.0.0.0", env="HOST", description="Server host")
    port: int = Field(8000, env="PORT", description="Server port")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Create global settings instance
settings = Settings()

# Backward compatibility with existing code
AZURE_OPENAI_ENDPOINT = settings.azure_openai_endpoint
AZURE_OPENAI_KEY = settings.azure_openai_key
AZURE_OPENAI_DEPLOYMENT_NAME = settings.azure_openai_deployment_name
AZURE_OPENAI_API_VERSION = settings.azure_openai_api_version
