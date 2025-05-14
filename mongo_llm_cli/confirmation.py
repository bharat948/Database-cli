"""Confirmation handler for destructive operations."""

import sys
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Set

import click

# Set of destructive operation names that require confirmation
DESTRUCTIVE_OPERATIONS: Set[str] = {
    "drop_collection", 
    "drop_index", 
    "delete_documents"
}


@contextmanager
def confirmation(tool_name: str, args: Dict[str, Any]) -> Iterator[None]:
    """
    Context manager that prompts for confirmation before executing destructive operations.

    Args:
        tool_name: The name of the tool being called.
        args: The arguments being passed to the tool.

    Yields:
        None: Context manager yields nothing.

    Raises:
        click.Abort: If the user doesn't confirm a destructive operation.
    """
    if tool_name in DESTRUCTIVE_OPERATIONS:
        # Format the operation for display
        op_description = f"{tool_name}"
        if "collection" in args:
            op_description += f" on collection '{args['collection']}'"
        
        # Format the args for display
        args_str = ", ".join([f"{k}={v}" for k, v in args.items() if k != "collection"])
        if args_str:
            op_description += f" with {args_str}"
        
        # Prompt for confirmation
        confirmed = click.confirm(
            f"This operation will {_get_operation_description(tool_name)}. "
            f"Are you sure you want to {op_description}?",
            default=False
        )
        
        if not confirmed:
            click.echo("Operation aborted.")
            raise click.Abort()
    
    yield


def _get_operation_description(tool_name: str) -> str:
    """Get a user-friendly description of the operation."""
    descriptions = {
        "drop_collection": "permanently delete a collection and all its documents",
        "drop_index": "remove an index from a collection",
        "delete_documents": "permanently delete multiple documents"
    }
    
    return descriptions.get(tool_name, "perform a destructive operation") 