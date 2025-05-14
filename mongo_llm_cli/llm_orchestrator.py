"""Orchestrator for communicating with LLM APIs."""

import inspect
import json
from typing import Any, Dict, List

import google.generativeai as genai

from mongo_llm_cli.mongodb_tool import MongoDBTool
from mongo_llm_cli.formatter import DateTimeEncoder


def build_tool_schema() -> Dict[str, Any]:
    """
    Build a JSON schema for the MongoDBTool methods.

    Returns:
        Dict[str, Any]: Schema describing tool methods, their parameters, and return types.
    """
    tool_schema = {"methods": []}
    
    # Collect methods from MongoDBTool
    methods = inspect.getmembers(
        MongoDBTool,
        predicate=lambda m: inspect.isfunction(m) and not m.__name__.startswith("_")
    )
    
    for name, method in methods:
        method_sig = inspect.signature(method)
        docstring = inspect.getdoc(method) or ""
        
        # Parse parameter information
        parameters = []
        for param_name, param in method_sig.parameters.items():
            if param_name == "self":
                continue
                
            param_type = str(param.annotation).replace("<class '", "").replace("'>", "")
            if param_type == "_empty":
                param_type = "Any"
                
            parameters.append({
                "name": param_name,
                "type": param_type,
                "default": str(param.default) if param.default is not inspect.Parameter.empty else None,
                "required": param.default is inspect.Parameter.empty
            })
        
        # Parse return type
        return_type = str(method_sig.return_annotation).replace("<class '", "").replace("'>", "")
        if return_type == "_empty":
            return_type = "None"
            
        # Add to schema
        tool_schema["methods"].append({
            "name": name,
            "description": docstring,
            "parameters": parameters,
            "return_type": return_type
        })
    
    return tool_schema


def construct_prompt(query: str, schema: Dict[str, Any], tool_schema: Dict[str, Any]) -> str:
    """
    Construct a prompt for the LLM with the user's query and context.

    Args:
        query: The natural language query from the user.
        schema: Database schema information from schema_inspector.
        tool_schema: Tool definitions from build_tool_schema.

    Returns:
        str: A prompt for the LLM.
    """
    prompt = f"""You are a database assistant. Given:
  • Available tools: {json.dumps(tool_schema, indent=2)}
  • Database schema context: {json.dumps(schema, indent=2, cls=DateTimeEncoder)}
  • User query: "{query}"

Return a JSON object: {{ "tool": <tool_name>, "args": {{ ... }} }}

Important:
1. Only select from the available tools. Don't invent new ones.
2. Make sure all required parameters for the chosen tool are provided.
3. For destructive operations (drop, delete), be absolutely certain this is what the user wants.
4. Return only valid JSON without any explanations or additional text.
"""
    return prompt


def call_llm(query: str, schema: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Call the Google Gemini LLM with the user's query and context.

    Args:
        query: The natural language query from the user.
        schema: Database schema information.
        api_key: Google Gemini API key.

    Returns:
        Dict[str, Any]: The parsed JSON response from the LLM.
    """
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    # Build tool schema
    tool_schema = build_tool_schema()
    
    # Construct prompt
    prompt = construct_prompt(query, schema, tool_schema)
    
    # Call the LLM
    response = model.generate_content(prompt)
    # print("this is the response from llm ",response)
    # Parse the response
    try:
        # Extract JSON string from the response
        response_text = response.text
        # Remove any markdown code block markers if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        # Parse JSON
        parsed_response = json.loads(response_text)
        return parsed_response
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {str(e)}\nResponse: {response.text}")
