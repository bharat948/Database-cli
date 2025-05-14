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
        
    def _serialize_document(self, doc: Dict) -> Dict:
        """Serialize a single MongoDB document to JSON-compatible format."""
        serialized_doc = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                serialized_doc[key] = str(value)
            # Add handling for other BSON types if necessary (e.g., datetime)
            # For example, to convert datetime objects to ISO format strings:
            # elif isinstance(value, datetime.datetime):
            #     serialized_doc[key] = value.isoformat()
            else:
                serialized_doc[key] = value
        return serialized_doc

    def _serialize_documents(self, cursor_or_list: Union[pymongo.cursor.Cursor, List[Dict]]) -> List[Dict]:
        """
        Serialize MongoDB documents from a cursor or list to JSON-compatible format.
        
        Args:
            cursor_or_list: MongoDB cursor or list containing documents.
            
        Returns:
            List[Dict]: Serialized documents.
        """
        result = []
        for doc in cursor_or_list: # Works for both cursor and list
            result.append(self._serialize_document(doc))
        return result

    def aggregate_documents(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        """
        Run an aggregation pipeline on a collection.

        Args:
            collection: Name of the collection.
            pipeline: List of aggregation pipeline stages.

        Returns:
            List[Dict]: Aggregation results.
        """
        cursor = self.db[collection].aggregate(pipeline)
        return list(self._serialize_documents(cursor))

    def count_documents(self, collection: str, filter: Dict) -> int:
        """
        Count the number of documents matching a filter.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.

        Returns:
            int: Number of matching documents.
        """
        filter = self._process_object_ids(filter)
        return self.db[collection].count_documents(filter)

    def distinct_values(self, collection: str, field: str, filter: Optional[Dict] = None) -> List[Any]:
        """
        Get all distinct values for a field in a collection.

        Args:
            collection: Name of the collection.
            field: Field name for which to return distinct values.
            filter: Optional filter to apply before getting distinct values.

        Returns:
            List[Any]: List of distinct values.
        """
        filter = self._process_object_ids(filter) if filter else {}
        return self.db[collection].distinct(field, filter)

    def rename_collection(self, old_name: str, new_name: str) -> None:
        """
        Rename a collection.

        Args:
            old_name: Current name of the collection.
            new_name: New name for the collection.
        """
        self.db[old_name].rename(new_name)

    def get_collection_stats(self, collection: str) -> Dict:
        """
        Get statistics about a collection.

        Args:
            collection: Name of the collection.

        Returns:
            Dict: Collection statistics.
        """
        return self.db.command("collstats", collection)

    def bulk_write(self, collection: str, operations: List[Dict]) -> Dict:
        """
        Perform bulk write operations (insert, update, delete).

        Args:
            collection: Name of the collection.
            operations: List of operations (dicts with 'type' and relevant fields).

        Returns:
            Dict: Bulk write result summary.
        """
        from pymongo import InsertOne, UpdateOne, DeleteOne

        ops = []
        for op in operations:
            if op["type"] == "insert":
                ops.append(InsertOne(op["document"]))
            elif op["type"] == "update":
                ops.append(UpdateOne(op["filter"], op["update"]))
            elif op["type"] == "delete":
                ops.append(DeleteOne(op["filter"]))
        result = self.db[collection].bulk_write(ops)
        return {
            "inserted_count": result.inserted_count,
            "modified_count": result.modified_count,
            "deleted_count": result.deleted_count,
            "upserted_count": result.upserted_count,
        }

    def find_one_document(
        self, collection: str, filter: Dict, projection: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Find a single document in a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.
            projection: Optional. A dictionary specifying which fields to include or exclude.
                        Example: {"name": 1, "email": 1, "_id": 0}

        Returns:
            Optional[Dict]: The matching document, or None if no document is found.
                            ObjectId fields are serialized to strings.
        """
        filter = self._process_object_ids(filter)
        document = self.db[collection].find_one(filter, projection)
        if document:
            return self._serialize_document(document)
        return None

    def insert_many_documents(self, collection: str, documents: List[Dict]) -> List[str]:
        """
        Insert multiple documents into a collection.

        Args:
            collection: Name of the collection.
            documents: A list of documents to insert.

        Returns:
            List[str]: A list of string representations of the _ids of the inserted documents.
        """
        if not documents:
            return []
        result = self.db[collection].insert_many(documents)
        return [str(inserted_id) for inserted_id in result.inserted_ids]

    def update_one_document(
        self, collection: str, filter: Dict, update: Dict, upsert: bool = False
    ) -> Dict:
        """
        Update a single document in a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.
            update: MongoDB update operations (e.g., using $set, $inc).
            upsert: If True, creates a new document if no document matches the filter. Default is False.

        Returns:
            Dict: A dictionary containing:
                  - 'matched_count': Number of documents matched.
                  - 'modified_count': Number of documents modified.
                  - 'upserted_id': The _id of the upserted document if an upsert occurred, else None.
                                   The _id is returned as a string.
        """
        filter = self._process_object_ids(filter)
        result = self.db[collection].update_one(filter, update, upsert=upsert)
        upserted_id_str = str(result.upserted_id) if result.upserted_id else None
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": upserted_id_str,
        }

    def delete_one_document(self, collection: str, filter: Dict) -> int:
        """
        Delete a single document from a collection.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.

        Returns:
            int: The number of documents deleted (0 or 1).
        """
        filter = self._process_object_ids(filter)
        result = self.db[collection].delete_one(filter)
        return result.deleted_count

    def find_one_and_update(
        self,
        collection: str,
        filter: Dict,
        update: Dict,
        projection: Optional[Dict] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        upsert: bool = False,
        return_document: str = "before",
    ) -> Optional[Dict]:
        """
        Atomically find a single document and update it.

        Args:
            collection: Name of the collection.
            filter: MongoDB filter query.
            update: MongoDB update operations.
            projection: Optional. Specifies which fields to return.
            sort: Optional. Specifies the order if multiple documents match the filter.
                  Example: [("age", pymongo.DESCENDING)]
            upsert: Optional. If True, creates a new document if no match is found. Default False.
            return_document: Optional. Specifies whether to return the document
                             as it was "before" the update or "after".
                             Accepts "before" or "after". Default "before".

        Returns:
            Optional[Dict]: The document (with ObjectIds serialized to strings)
                            or None if no document matches (and upsert is False).
        """
        from pymongo import ReturnDocument

        filter = self._process_object_ids(filter)
        
        return_doc_option = ReturnDocument.BEFORE
        if return_document.lower() == "after":
            return_doc_option = ReturnDocument.AFTER

        doc = self.db[collection].find_one_and_update(
            filter,
            update,
            projection=projection,
            sort=sort,
            upsert=upsert,
            return_document=return_doc_option,
        )
        if doc:
            return self._serialize_document(doc)
        return None

    def run_command(self, command: Union[Dict, str], **kwargs) -> Dict:
        """
        Run a database command.

        Args:
            command: The command to run (e.g., "ping", {"buildInfo": 1}).
            **kwargs: Additional arguments for the command.

        Returns:
            Dict: The result of the command. ObjectIds and other BSON types
                  (like datetime) are serialized where possible.
        """
        raw_result = self.db.command(command, **kwargs)

        # Recursively serialize known BSON types to JSON-friendly formats.
        def serialize_value(value: Any) -> Any:
            if isinstance(value, ObjectId):
                return str(value)
            elif isinstance(value, list):
                return [serialize_value(v) for v in value]
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            # Example: Add datetime serialization if needed
            # import datetime # Add to top-level imports if used here
            # from bson.datetime_ms import DatetimeMS # Add to top-level imports if used here
            # if isinstance(value, datetime.datetime) or isinstance(value, DatetimeMS):
            #    return value.isoformat()
            return value

        return serialize_value(raw_result)
