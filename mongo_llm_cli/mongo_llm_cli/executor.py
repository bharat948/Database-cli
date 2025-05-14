"""Executor for MongoDB tool calls."""

from typing import Any, Dict, Optional

from mongo_llm_cli.mongodb_tool import MongoDBTool
from mongo_llm_cli.query_translator import ParsedQuery


def execute(tool: MongoDBTool, parsed_query: ParsedQuery) -> Dict[str, Any]:
    """
    Execute a parsed query against the MongoDB tool.

    Args:
        tool: The MongoDB tool instance.
        parsed_query: The parsed query to execute.

    Returns:
        Dict[str, Any]: Result of the execution with:
            - success: Boolean indicating success or failure
            - data: Result data (if successful)
            - error: Error message (if unsuccessful)
    """
    try:
        # Get the method to call
        method_name = parsed_query.tool
        method = getattr(tool, method_name, None)
        
        if method is None:
            return {
                "success": False,
                "error": f"Unknown method: {method_name}",
                "data": None,
            }
        
        # Call the method with the provided arguments
        result = method(**parsed_query.args)
        
        return {
            "success": True,
            "data": result,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
        } 