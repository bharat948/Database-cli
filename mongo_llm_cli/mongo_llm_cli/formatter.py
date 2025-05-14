"""Formatter for pretty-printing MongoDB CLI results."""

import json
from typing import Any, Dict, List, Union

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

    # Check if list contains dictionaries
    if all(isinstance(item, dict) for item in items):
        print_table(items)
    else:
        # Print simple list
        for i, item in enumerate(items, 1):
            click.echo(f"{i}. {_format_item(item)}")


def print_dict(data: Dict) -> None:
    """Print a dictionary."""
    if not data:
        click.echo("Empty result.")
        return

    formatted_json = json.dumps(data, indent=2, default=str)
    click.echo(formatted_json)


def print_table(items: List[Dict]) -> None:
    """Print a list of dictionaries as a table."""
    if not items:
        click.echo("No items found.")
        return

    # Find all unique keys
    all_keys = set()
    for item in items:
        all_keys.update(item.keys())

    # Select a subset of keys if there are too many
    MAX_COLUMNS = 5
    keys_to_show = list(all_keys)
    if len(keys_to_show) > MAX_COLUMNS:
        # Prioritize common identifier fields
        priority_keys = ["_id", "id", "name", "title"]
        sorted_keys = sorted(
            keys_to_show,
            key=lambda k: (0 if k in priority_keys else 1, priority_keys.index(k) if k in priority_keys else 999)
        )
        keys_to_show = sorted_keys[:MAX_COLUMNS]
        click.echo(click.style(f"Showing {MAX_COLUMNS} of {len(all_keys)} fields. Use JSON format to see all fields.", fg="yellow"))

    # Print header
    header = " | ".join([k.upper() for k in keys_to_show])
    click.echo(click.style(header, bold=True))
    click.echo("-" * len(header))

    # Print rows
    for item in items:
        row_values = []
        for key in keys_to_show:
            value = item.get(key, "")
            # Truncate long values
            value_str = _format_item(value)
            if len(value_str) > 30:
                value_str = value_str[:27] + "..."
            row_values.append(value_str)
        click.echo(" | ".join(row_values))


def _format_item(item: Any) -> str:
    """Format an item for display."""
    if isinstance(item, dict):
        return json.dumps(item, default=str)
    elif isinstance(item, list):
        if len(item) > 3:
            return f"[{', '.join(str(x) for x in item[:3])}... +{len(item)-3} more]"
        else:
            return str(item)
    else:
        return str(item) 