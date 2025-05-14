"""Configuration management for the MongoDB LLM CLI."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for the MongoDB LLM CLI."""

    mongo_uri: str
    mongo_db_name: str
    gemini_api_key: str


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables or .env file.

    Args:
        config_path: Optional path to a .env file. If not provided,
                    the default .env file in the current directory is used.

    Returns:
        Config: Configuration object with all required settings.

    Raises:
        ValueError: If any required configuration value is missing.
    """
    if config_path:
        if not os.path.exists(config_path):
            raise ValueError(f"Config file not found: {config_path}")
        load_dotenv(config_path)
    else:
        # Try to load from .env in the current directory
        default_env_path = Path(".env")
        if default_env_path.exists():
            load_dotenv(default_env_path)

    # Get required configuration values
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db_name = os.getenv("MONGO_DB_NAME")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    # Validate configuration
    missing = []
    if not mongo_uri:
        missing.append("MONGO_URI")
    if not mongo_db_name:
        missing.append("MONGO_DB_NAME")
    if not gemini_api_key:
        missing.append("GEMINI_API_KEY")

    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}. "
            f"Please set these in your environment or .env file."
        )

    return Config(
        mongo_uri=mongo_uri,
        mongo_db_name=mongo_db_name,
        gemini_api_key=gemini_api_key,
    ) 