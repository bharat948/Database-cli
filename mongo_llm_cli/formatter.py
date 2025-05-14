"""Formatter for pretty-printing MongoDB CLI results."""

import json
from json import JSONEncoder
from typing import Any, Dict, List, Union
from datetime import datetime
from bson.objectid import ObjectId

import click


def print(result: Dict[str, Any]) -> None:
    """
    Print the result of a MongoDB operation.

    Args:
        result: The result to print, containing:
            - success: Boolean indicating success or failure
            - data: Result data (if successful)
            - error: Error message (if unsuccessful)
    """
    if not result["success"]:
        print_error(result["error"])
        return

    if result["data"] is None:
        click.echo(click.style("Operation completed successfully with no data.", fg="green"))
        return

    data = result["data"]
    data_type = type(data)

    if isinstance(data, list):
        print_list(data)
    elif isinstance(data, dict):
        print_dict(data)
    elif isinstance(data, str):
        if data.startswith(("{", "[")):  # Detect if it might be JSON string
            try:
                json_data = json.loads(data)
                print_dict(json_data) if isinstance(json_data, dict) else print_list(json_data)
            except json.JSONDecodeError:
                click.echo(data)
        else:
            click.echo(data)
    elif isinstance(data, (int, float, bool)):
        # For simple types like count of documents affected
        click.echo(str(data))
    else:
        # Fallback for anything else
        click.echo(str(data))


def print_error(error: str) -> None:
    """Print an error message."""
    click.echo(click.style(f"Error: {error}", fg="red", bold=True))


def print_list(items: List) -> None:
    """Print a list of items."""
    if not items:
        click.echo("No items found.")
        return

    # Check if list contains dictionaries or other complex objects
    if all(isinstance(item, (dict, list)) for item in items):
        # Print full JSON for lists of dictionaries or lists
        formatted_json = json.dumps(items, indent=2, cls=DateTimeEncoder)
        click.echo(formatted_json)
    else:
        # Print simple list
        for i, item in enumerate(items, 1):
            click.echo(f"{i}. {_format_item(item)}")


class DateTimeEncoder(JSONEncoder):
    """Custom JSONEncoder to handle datetime and ObjectId objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def print_dict(data: Dict) -> None:
    """Print a dictionary as JSON."""
    if not data:
        click.echo("Empty result.")
        return

    formatted_json = json.dumps(data, indent=2, cls=DateTimeEncoder)
    click.echo(formatted_json)


def _format_item(item: Any) -> str:
    """Format an item for display."""
    if isinstance(item, dict):
        # For nested dictionaries within a list, format as a compact JSON string
        return json.dumps(item, default=str)
    elif isinstance(item, list):
        # For nested lists within a list, format as a compact string
        if len(item) > 3:
            return f"[{', '.join(str(x) for x in item[:3])}... +{len(item)-3} more]"
        else:
            return str(item)
    elif isinstance(item, datetime):
        return item.isoformat()
    elif isinstance(item, ObjectId):
        return str(item)
    else:
        return str(item)
