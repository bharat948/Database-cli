"""Translator for LLM responses to executable tool calls."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ParsedQuery:
    """Parsed query from the LLM."""

    tool: str
    args: Dict[str, Any]


def translate(llm_response: Dict[str, Any]) -> ParsedQuery:
    """
    Translate an LLM response into a parsed query.

    Args:
        llm_response: The response from the LLM.

    Returns:
        ParsedQuery: Parsed query with tool name and arguments.

    Raises:
        ValueError: If the response is invalid or missing required fields.
    """
    if not isinstance(llm_response, dict):
        raise ValueError(f"Expected a dictionary response, got: {type(llm_response)}")

    # Check for required fields
    if "tool" not in llm_response:
        raise ValueError("Missing 'tool' field in LLM response")
    
    if "args" not in llm_response:
        raise ValueError("Missing 'args' field in LLM response")
    
    tool_name = llm_response["tool"]
    args = llm_response["args"]
    
    # Validate args is a dictionary
    if not isinstance(args, dict):
        raise ValueError(f"Expected 'args' to be a dictionary, got: {type(args)}")
    
    return ParsedQuery(tool=tool_name, args=args) 