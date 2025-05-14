"""Command-line interface for the MongoDB LLM CLI."""

import sys
from typing import Optional, Tuple

import click

from mongo_llm_cli import llm_orchestrator
from mongo_llm_cli.config import get_config
from mongo_llm_cli.confirmation import confirmation
from mongo_llm_cli.executor import execute
from mongo_llm_cli.formatter import print as format_print
from mongo_llm_cli.mongodb_tool import MongoDBTool
from mongo_llm_cli.query_translator import translate
from mongo_llm_cli.schema_inspector import inspect_schema


@click.group()
@click.option(
    "--config",
    "-c",
    help="Path to a configuration file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.pass_context
def mongo_llm(ctx: click.Context, config: Optional[str] = None) -> None:
    """MongoDB Natural Language CLI tool.

    This tool allows you to interact with MongoDB using natural language queries.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


@mongo_llm.command()
@click.pass_context
def test_connection(ctx: click.Context) -> None:
    """Test the MongoDB connection."""
    try:
        config = get_config(ctx.obj.get("config_path"))
        tool = MongoDBTool(config.mongo_uri, config.mongo_db_name)
        
        # Try to list collections to verify connection works
        collections = tool.list_collections()
        
        click.echo(click.style("✓ Connection successful!", fg="green", bold=True))
        click.echo(f"Connected to database: {config.mongo_db_name}")
        if collections:
            click.echo(f"Available collections: {', '.join(collections)}")
        else:
            click.echo("No collections found in the database.")
    except Exception as e:
        click.echo(click.style(f"✗ Connection failed: {str(e)}", fg="red", bold=True))
        sys.exit(1)


@mongo_llm.command()
@click.argument("nl_query", nargs=-1)
@click.pass_context
def run(ctx: click.Context, nl_query: Tuple[str, ...]) -> None:
    """Run a natural language query against MongoDB."""
    if not nl_query:
        click.echo(click.style("Error: No query provided.", fg="red"))
        click.echo("Usage: mongo-llm run \"your natural language query\"")
        sys.exit(1)
        
    query = " ".join(nl_query)
    
    try:
        # Get configuration
        config = get_config(ctx.obj.get("config_path"))
        
        # Initialize MongoDB tool
        tool = MongoDBTool(config.mongo_uri, config.mongo_db_name)
        
        # Inspect database schema
        click.echo("Inspecting database schema...")
        schema = inspect_schema(tool)
        
        # Call LLM
        click.echo("Processing your query...")
        resp = llm_orchestrator.call_llm(query, schema, config.gemini_api_key)
        
        # Parse response
        parsed = translate(resp)
        
        # Execute with confirmation for destructive operations
        click.echo(f"Executing: {parsed.tool}")
        with confirmation(parsed.tool, parsed.args):
            result = execute(tool, parsed)
            
        # Format and print the result
        format_print(result)
        
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    mongo_llm(obj={}) 