"""Tests for the configuration module."""

import os
import tempfile
from unittest import mock

import pytest

from mongo_llm_cli.config import get_config, Config


def test_get_config_from_env():
    """Test loading configuration from environment variables."""
    # Mock environment variables
    with mock.patch.dict(os.environ, {
        "MONGO_URI": "mongodb://user:pass@localhost:27017",
        "MONGO_DB_NAME": "test_db",
        "GEMINI_API_KEY": "fake_api_key",
    }):
        # Get config
        config = get_config()
        
        # Assert values
        assert isinstance(config, Config)
        assert config.mongo_uri == "mongodb://user:pass@localhost:27017"
        assert config.mongo_db_name == "test_db"
        assert config.gemini_api_key == "fake_api_key"


def test_get_config_from_file():
    """Test loading configuration from a file."""
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("MONGO_URI=mongodb://user:pass@localhost:27017\n")
        temp_file.write("MONGO_DB_NAME=test_db\n")
        temp_file.write("GEMINI_API_KEY=fake_api_key\n")
        temp_path = temp_file.name
        
    try:
        # Get config from the file
        config = get_config(temp_path)
        
        # Assert values
        assert isinstance(config, Config)
        assert config.mongo_uri == "mongodb://user:pass@localhost:27017"
        assert config.mongo_db_name == "test_db"
        assert config.gemini_api_key == "fake_api_key"
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_missing_config():
    """Test error when configuration is missing."""
    # Mock empty environment
    with mock.patch.dict(os.environ, clear=True):
        # Expect ValueError
        with pytest.raises(ValueError) as excinfo:
            get_config()
        
        # Check if the error message contains the missing fields
        error_msg = str(excinfo.value)
        assert "MONGO_URI" in error_msg
        assert "MONGO_DB_NAME" in error_msg
        assert "GEMINI_API_KEY" in error_msg


def test_config_file_not_found():
    """Test error when configuration file not found."""
    with pytest.raises(ValueError) as excinfo:
        get_config("nonexistent_file.env")
    
    assert "not found" in str(excinfo.value) 