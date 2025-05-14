"""Tests for the MongoDB tool."""

from unittest import mock

import pytest
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from mongo_llm_cli.mongodb_tool import MongoDBTool


@pytest.fixture
def mock_mongodb():
    """Fixture for mocking MongoDB client, database, and collections."""
    with mock.patch("pymongo.MongoClient") as mock_client:
        # Mock the database
        mock_db = mock.MagicMock(spec=Database)
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Mock a collection
        mock_collection = mock.MagicMock(spec=Collection)
        mock_db.__getitem__.return_value = mock_collection
        
        # Set up common return values
        mock_db.list_collection_names.return_value = ["users", "products"]
        
        yield mock_client, mock_db, mock_collection


def test_list_collections(mock_mongodb):
    """Test listing collections."""
    _, mock_db, _ = mock_mongodb
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    collections = tool.list_collections()
    
    # Assert
    assert collections == ["users", "products"]
    mock_db.list_collection_names.assert_called_once()


def test_create_collection(mock_mongodb):
    """Test creating a collection."""
    _, mock_db, _ = mock_mongodb
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    tool.create_collection("new_collection")
    
    # Assert
    mock_db.create_collection.assert_called_once_with("new_collection")


def test_drop_collection(mock_mongodb):
    """Test dropping a collection."""
    _, _, mock_collection = mock_mongodb
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    tool.drop_collection("users")
    
    # Assert
    mock_collection.drop.assert_called_once()


def test_list_indexes(mock_mongodb):
    """Test listing indexes."""
    _, _, mock_collection = mock_mongodb
    
    # Mock indexes
    mock_indexes = [
        {"name": "_id_", "key": [("_id", 1)]},
        {"name": "email_1", "key": [("email", 1)], "unique": True}
    ]
    mock_collection.list_indexes.return_value = mock_indexes
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    indexes = tool.list_indexes("users")
    
    # Assert
    assert indexes == mock_indexes
    mock_collection.list_indexes.assert_called_once()


def test_create_index(mock_mongodb):
    """Test creating an index."""
    _, _, mock_collection = mock_mongodb
    mock_collection.create_index.return_value = "email_1"
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    index_name = tool.create_index("users", [("email", 1)], unique=True)
    
    # Assert
    assert index_name == "email_1"
    mock_collection.create_index.assert_called_once_with([("email", 1)], unique=True)


def test_drop_index(mock_mongodb):
    """Test dropping an index."""
    _, _, mock_collection = mock_mongodb
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    tool.drop_index("users", "email_1")
    
    # Assert
    mock_collection.drop_index.assert_called_once_with("email_1")


def test_insert_document(mock_mongodb):
    """Test inserting a document."""
    _, _, mock_collection = mock_mongodb
    mock_id = ObjectId("5f50c31e8a91e73550a97d5f")
    mock_collection.insert_one.return_value = InsertOneResult(mock_id, acknowledged=True)
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    doc = {"name": "John", "email": "john@example.com"}
    result = tool.insert_document("users", doc)
    
    # Assert
    assert result == str(mock_id)
    mock_collection.insert_one.assert_called_once_with(doc)


def test_find_documents(mock_mongodb):
    """Test finding documents."""
    _, _, mock_collection = mock_mongodb
    mock_docs = [
        {"_id": ObjectId("5f50c31e8a91e73550a97d5f"), "name": "John"},
        {"_id": ObjectId("5f50c31e8a91e73550a97d60"), "name": "Jane"}
    ]
    mock_collection.find.return_value.limit.return_value = mock_docs
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    filter_query = {"name": "J"}
    docs = tool.find_documents("users", filter_query, limit=2)
    
    # Assert
    assert len(docs) == 2
    assert docs[0]["_id"] == str(mock_docs[0]["_id"])
    assert docs[1]["name"] == "Jane"
    mock_collection.find.assert_called_once_with(filter_query)
    mock_collection.find.return_value.limit.assert_called_once_with(2)


def test_update_documents(mock_mongodb):
    """Test updating documents."""
    _, _, mock_collection = mock_mongodb
    mock_collection.update_many.return_value = UpdateResult(
        {"n": 2, "nModified": 2}, acknowledged=True
    )
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    filter_query = {"active": False}
    update = {"$set": {"active": True}}
    result = tool.update_documents("users", filter_query, update)
    
    # Assert
    assert result == 2
    mock_collection.update_many.assert_called_once_with(filter_query, update)


def test_delete_documents(mock_mongodb):
    """Test deleting documents."""
    _, _, mock_collection = mock_mongodb
    mock_collection.delete_many.return_value = DeleteResult({"n": 3}, acknowledged=True)
    
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Call method
    filter_query = {"status": "inactive"}
    result = tool.delete_documents("users", filter_query)
    
    # Assert
    assert result == 3
    mock_collection.delete_many.assert_called_once_with(filter_query)


def test_process_object_ids():
    """Test processing of ObjectId values in queries."""
    # Create tool instance
    tool = MongoDBTool("mongodb://localhost:27017", "test_db")
    
    # Test with string _id
    query = {"_id": "5f50c31e8a91e73550a97d5f"}
    processed = tool._process_object_ids(query)
    assert isinstance(processed["_id"], ObjectId)
    assert str(processed["_id"]) == "5f50c31e8a91e73550a97d5f"
    
    # Test with $in operator
    query = {"_id": {"$in": ["5f50c31e8a91e73550a97d5f", "5f50c31e8a91e73550a97d60"]}}
    processed = tool._process_object_ids(query)
    assert isinstance(processed["_id"]["$in"][0], ObjectId)
    assert len(processed["_id"]["$in"]) == 2
    
    # Test with invalid ObjectId string (should remain unchanged)
    query = {"_id": "invalid-object-id"}
    processed = tool._process_object_ids(query)
    assert processed["_id"] == "invalid-object-id" 