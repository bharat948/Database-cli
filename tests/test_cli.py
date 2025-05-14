"""Tests for the CLI module."""

from unittest import mock

import pytest
from click.testing import CliRunner

from mongo_llm_cli.cli import mongo_llm


@pytest.fixture
def runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Mock the configuration."""
    with mock.patch("mongo_llm_cli.cli.get_config") as mock_get_config:
        # Create a mock config object
        mock_config = mock.MagicMock()
        mock_config.mongo_uri = "mongodb://localhost:27017"
        mock_config.mongo_db_name = "test_db"
        mock_config.gemini_api_key = "fake_api_key"
        
        # Set the return value of get_config
        mock_get_config.return_value = mock_config
        
        yield mock_get_config


@pytest.fixture
def mock_mongodb_tool():
    """Mock the MongoDB tool."""
    with mock.patch("mongo_llm_cli.cli.MongoDBTool") as mock_tool_class:
        # Create a mock tool instance
        mock_tool = mock.MagicMock()
        mock_tool.list_collections.return_value = ["users", "products"]
        
        # Set the return value of the constructor
        mock_tool_class.return_value = mock_tool
        
        yield mock_tool


def test_test_connection_success(runner, mock_config, mock_mongodb_tool):
    """Test successful connection test."""
    # Run the command
    result = runner.invoke(mongo_llm, ["test-connection"])
    
    # Check success
    assert result.exit_code == 0
    assert "Connection successful" in result.output
    assert "users, products" in result.output


def test_test_connection_failure(runner, mock_config, mock_mongodb_tool):
    """Test failed connection test."""
    # Make the list_collections method raise an exception
    mock_mongodb_tool.list_collections.side_effect = Exception("Connection failed")
    
    # Run the command
    result = runner.invoke(mongo_llm, ["test-connection"])
    
    # Check failure
    assert result.exit_code == 1
    assert "Connection failed" in result.output


@mock.patch("mongo_llm_cli.cli.inspect_schema")
@mock.patch("mongo_llm_cli.cli.llm_orchestrator.call_llm")
@mock.patch("mongo_llm_cli.cli.translate")
@mock.patch("mongo_llm_cli.cli.execute")
@mock.patch("mongo_llm_cli.cli.format_print")
def test_run_command(
    mock_format_print, mock_execute, mock_translate, mock_call_llm, mock_inspect_schema,
    runner, mock_config, mock_mongodb_tool
):
    """Test the run command."""
    # Set up mock returns
    mock_inspect_schema.return_value = {"collections": ["users"]}
    mock_call_llm.return_value = {"tool": "list_collections", "args": {}}
    mock_parsed_query = mock.MagicMock()
    mock_parsed_query.tool = "list_collections"
    mock_parsed_query.args = {}
    mock_translate.return_value = mock_parsed_query
    mock_execute.return_value = {"success": True, "data": ["users"], "error": None}
    
    # Run the command
    result = runner.invoke(mongo_llm, ["run", "list all collections"])
    
    # Check success
    assert result.exit_code == 0
    assert "Processing your query" in result.output
    assert "Executing: list_collections" in result.output
    
    # Verify mock calls
    mock_inspect_schema.assert_called_once_with(mock_mongodb_tool)
    mock_call_llm.assert_called_once_with(
        "list all collections",
        mock_inspect_schema.return_value,
        mock_config.return_value.gemini_api_key
    )
    mock_translate.assert_called_once_with(mock_call_llm.return_value)
    mock_execute.assert_called_once_with(mock_mongodb_tool, mock_translate.return_value)
    mock_format_print.assert_called_once_with(mock_execute.return_value)


def test_run_command_no_query(runner):
    """Test the run command with no query."""
    # Run the command without a query
    result = runner.invoke(mongo_llm, ["run"])
    
    # Check failure
    assert result.exit_code == 1
    assert "Error: No query provided" in result.output 