"""MongoDB interaction tools."""

from typing import Dict, List, Optional, Tuple, Any, Union

import pymongo
from bson.objectid import ObjectId


class MongoDBTool:
    """Tool for interacting with MongoDB databases."""

    def __init__(self, uri: str, db_name: str):
        """
        Initialize the MongoDB tool.

        Args:
            uri: MongoDB connection URI.
            db_name: Name of the database to use.
        """
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List[str]: A list of collection names.
        """
        return self.db.list_collection_names()

    def create_collection(self, name: str) -> None:
        """
        Create a new collection.

        Args:
            name: Name of the collection to create.
        """
        self.db.create_collection(name)

    def drop_collection(self, name: str) -> None:
        """
        Drop a collection.

        Args:
            name: Name of the collection to drop.
        """
        self.db[name].drop()

    def list_indexes(self, collection: str) -> List[Dict]:
        """
        List all indexes for a collection.

        Args:
            collection: Name of the collection.

        Returns:
            List[Dict]: A list of index information dictionaries.
        """
        return list(self.db[collection].list_indexes())

    def create_index(
        self, collection: str, keys: List[Tuple[str, int]], **options
    ) -> str:
        """
        Create an index on a collection.

        Args:
            collection: Name of the collection.
            keys: List of (field_name, direction) pairs.
                 Direction is 1 for ascending, -1 for descending.
            **options: Additional index options like unique=True.

        Returns:
            str: Name of the created index.
        """
        return self.db[collection].create_index(keys, **options)

    def drop_index(self, collection: str, index_name: str) -> None:
        """
        Drop an index from a collection.

        Args:
            collection: Name of the collection.
            index_name: Name of the index to drop.
        """
        self.db[collection].drop_index(index_name)

    def insert_document(self, collection: str, document: Dict) -> str:
        """
        Insert a document into a collection.

        Args:
            collection: Name of the collection.
            document: The document to insert.

        Returns:
            str: ID of the inserted document.
        """
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)

    def find_documents(
        self, collection: str, filter: Dict, limit: int = 10
    ) -> List[Dict]:
        """
        Find documents in a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.
            limit: Maximum number of documents to return (default: 10).

        Returns:
            List[Dict]: List of matching documents.
        """
        # Convert ObjectId strings back to ObjectId objects
        filter = self._process_object_ids(filter)
        
        cursor = self.db[collection].find(filter).limit(limit)
        return list(self._serialize_documents(cursor))

    def update_documents(
        self, collection: str, filter: Dict, update: Dict
    ) -> int:
        """
        Update documents in a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.
            update: MongoDB update operations.

        Returns:
            int: Number of documents modified.
        """
        # Convert ObjectId strings back to ObjectId objects
        filter = self._process_object_ids(filter)
        
        result = self.db[collection].update_many(filter, update)
        return result.modified_count

    def delete_documents(self, collection: str, filter: Dict) -> int:
        """
        Delete documents from a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.

        Returns:
            int: Number of documents deleted.
        """
        # Convert ObjectId strings back to ObjectId objects
        filter = self._process_object_ids(filter)
        
        result = self.db[collection].delete_many(filter)
        return result.deleted_count

    def _process_object_ids(self, query: Dict) -> Dict:
        """
        Process a query dictionary to convert string '_id' to ObjectId.
        
        Args:
            query: The query dictionary.
            
        Returns:
            Dict: Processed query with ObjectId objects.
        """
        if not query:
            return query
            
        result = query.copy()
        if '_id' in result and isinstance(result['_id'], str):
            try:
                result['_id'] = ObjectId(result['_id'])
            except Exception:
                # If conversion fails, keep the original
                pass
                
        # Handle $in operator for _id
        if '_id' in result and isinstance(result['_id'], dict):
            if '$in' in result['_id'] and isinstance(result['_id']['$in'], list):
                result['_id']['$in'] = [
                    ObjectId(id_str) if isinstance(id_str, str) else id_str
                    for id_str in result['_id']['$in']
                ]
                
        return result
        
    def _serialize_documents(self, cursor) -> List[Dict]:
        """
        Serialize MongoDB documents to JSON-compatible format.
        
        Args:
            cursor: MongoDB cursor containing documents.
            
        Returns:
            List[Dict]: Serialized documents.
        """
        result = []
        for doc in cursor:
            serialized_doc = {}
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    serialized_doc[key] = str(value)
                else:
                    serialized_doc[key] = value
            result.append(serialized_doc)
        return result 