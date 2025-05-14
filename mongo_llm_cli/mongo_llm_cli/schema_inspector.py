"""MongoDB schema inspection utilities."""

from typing import Dict, List, Any

from mongo_llm_cli.mongodb_tool import MongoDBTool


def inspect_schema(tool: MongoDBTool) -> Dict[str, Any]:
    """
    Inspect the database schema and return a structured representation.

    This function examines collections in the database and collects
    sample documents to provide context about the data structure.

    Args:
        tool: Instance of MongoDBTool connected to a database.

    Returns:
        Dict[str, Any]: Dictionary containing collections and sample documents.
    """
    collections = tool.list_collections()
    schema = {
        "collections": collections,
        "sample_documents": {},
    }

    # Get one sample document from each collection
    for collection in collections:
        try:
            # Find one document in the collection
            sample = tool.find_documents(collection, {}, limit=1)
            if sample:
                schema["sample_documents"][collection] = sample[0]
            else:
                schema["sample_documents"][collection] = {}
        except Exception as e:
            # If there's an error getting a sample, log it and continue
            schema["sample_documents"][collection] = {"error": str(e)}

    return schema 