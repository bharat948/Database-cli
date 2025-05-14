# MongoDB LLM CLI Architecture

This document describes the architecture of the MongoDB LLM CLI tool.

## System Overview

The MongoDB LLM CLI tool is a command-line application that allows users to interact with MongoDB databases using natural language queries. The tool leverages the Google Gemini API to understand natural language queries and translate them into appropriate MongoDB operations.

## Architecture Diagram

```mermaid
graph TD
    A[CLI Input (NL Query)] --> B[CLI Handler]
    B --> C[Config Loader]
    B --> L[Confirmation Handler]
    B --> D[Schema Inspector]
    B --> E[LLM Orchestrator]
    E --> F[Gemini API]
    E --> G[Tool Definitions]
    F --> E
    B --> H[Query Translator]
    H --> I[Tool Executor]
    I --> J[MongoDBTool]
    I --> K[Result Formatter]
    K --> B
    J --> M[MongoDB]
```

## Module Descriptions

### `config.py`

The configuration module is responsible for loading environment variables and configuration settings from `.env` files. It provides a centralized way to access configuration values throughout the application.

**Key Components:**
- `Config` dataclass: Stores configuration values
- `get_config()` function: Loads configuration from environment or file

### `mongodb_tool.py`

The MongoDB Tool module provides a high-level interface for interacting with MongoDB databases. It wraps the PyMongo library and provides methods for common operations like listing collections, creating indexes, and manipulating documents.

**Key Components:**
- `MongoDBTool` class: Main class for MongoDB operations
- Methods for collection, index, and document management

### `schema_inspector.py`

The Schema Inspector module analyzes the MongoDB database to gather information about its structure, including collection names and sample documents. This information is used to provide context to the LLM.

**Key Components:**
- `inspect_schema()` function: Analyzes database structure

### `llm_orchestrator.py`

The LLM Orchestrator module is responsible for communicating with the Google Gemini API. It constructs prompts, sends them to the API, and processes the responses.

**Key Components:**
- `build_tool_schema()` function: Dynamically builds a schema of available tools
- `construct_prompt()` function: Creates a prompt for the LLM
- `call_llm()` function: Calls the Gemini API and processes responses

### `query_translator.py`

The Query Translator module parses the JSON responses from the LLM and validates them against the expected schema.

**Key Components:**
- `ParsedQuery` dataclass: Represents a parsed query
- `translate()` function: Validates and transforms LLM responses

### `executor.py`

The Executor module executes parsed queries against the MongoDB tool.

**Key Components:**
- `execute()` function: Calls the appropriate MongoDB tool method with arguments

### `confirmation.py`

The Confirmation module provides safeguards for destructive operations, prompting the user for confirmation before executing operations like dropping collections or deleting documents.

**Key Components:**
- `confirmation()` context manager: Handles confirmation prompts
- `DESTRUCTIVE_OPERATIONS` set: Defines operations requiring confirmation

### `formatter.py`

The Formatter module transforms the results of MongoDB operations into human-readable formats.

**Key Components:**
- `print()` function: Main formatting function
- Various specialized formatters for different data types

### `cli.py`

The CLI module provides the command-line interface for the application using the Click library.

**Key Components:**
- `mongo_llm` command group: Main entry point
- Command handlers for `test-connection` and `run`

## Data Flow

1. User enters a natural language query via the CLI
2. The CLI handler loads configuration and initializes components
3. Schema Inspector analyzes the database structure
4. LLM Orchestrator builds a prompt with schema context and user query
5. The prompt is sent to the Gemini API, which returns a JSON response
6. Query Translator validates the response and extracts tool name and arguments
7. For destructive operations, Confirmation Handler prompts for user approval
8. Executor calls the appropriate MongoDB Tool method with the extracted arguments
9. Result Formatter processes the result and displays it to the user

## Error Handling

The system uses a centralized error handling approach:

1. Low-level errors from MongoDB are caught and wrapped in the MongoDB Tool
2. LLM parsing errors are caught and reported with helpful messages
3. All errors bubble up to the CLI handler, which formats them for display
4. Critical errors result in clean process termination with non-zero exit codes

## Future Improvements

1. **Conversation Context**: Maintain context across multiple queries
2. **Query Templates**: Support for parameterized query templates
3. **Authentication**: Support for more authentication methods
4. **Web UI**: Add a web interface for easier interaction
5. **Extended MongoDB Support**: Support for more MongoDB operations like aggregation pipelines 