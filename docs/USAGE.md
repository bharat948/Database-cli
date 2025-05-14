# MongoDB LLM CLI Usage Guide

This document provides detailed usage instructions for the MongoDB LLM CLI tool.

## Command Reference

### General Structure

```
mongo-llm [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- `--config, -c`: Path to a configuration file (`.env` format)
  - Example: `mongo-llm -c /path/to/.env command`

### Commands

#### `test-connection`

Test the MongoDB connection specified in your configuration.

```
mongo-llm test-connection
```

Output:
```
✓ Connection successful!
Connected to database: your_db
Available collections: collection1, collection2, collection3
```

#### `run`

Run a natural language query against your MongoDB database.

```
mongo-llm run "your natural language query"
```

## Example Queries and Outputs

### Collection Management

#### Listing Collections

**Query**: `mongo-llm run "list all collections"`

**Output**:
```
1. users
2. products
3. orders
```

#### Creating a Collection

**Query**: `mongo-llm run "create a new collection called customers"`

**Output**:
```
Operation completed successfully with no data.
```

#### Dropping a Collection

**Query**: `mongo-llm run "drop the test_collection collection"`

**Output**:
```
This operation will permanently delete a collection and all its documents. 
Are you sure you want to drop_collection on collection 'test_collection'? [y/N]: y
Operation completed successfully with no data.
```

### Document Operations

#### Finding Documents

**Query**: `mongo-llm run "find the first 3 users where name starts with 'J'"`

**Output**:
```
_ID                     | NAME    | EMAIL                | AGE
---------------------------------------------------------
5f50c31e8a91e73550a97d5f | John    | john@example.com    | 30
5f50c31e8a91e73550a97d60 | Jane    | jane@example.com    | 25
5f50c31e8a91e73550a97d61 | James   | james@example.com   | 35
```

#### Inserting a Document

**Query**: `mongo-llm run "insert a new user with name 'Sarah', email 'sarah@example.com', and age 28"`

**Output**:
```
5f50c31e8a91e73550a97d62
```

#### Updating Documents

**Query**: `mongo-llm run "update all users with age less than 30 to set status as 'young'"`

**Output**:
```
2
```
(This indicates 2 documents were updated)

#### Deleting Documents

**Query**: `mongo-llm run "delete users with status 'inactive'"`

**Output**:
```
This operation will permanently delete multiple documents. 
Are you sure you want to delete_documents on collection 'users' with filter={'status': 'inactive'}? [y/N]: y
3
```
(This indicates 3 documents were deleted)

### Index Management

#### Listing Indexes

**Query**: `mongo-llm run "list indexes for the users collection"`

**Output**:
```
[
  {
    "v": 2,
    "key": {
      "_id": 1
    },
    "name": "_id_"
  },
  {
    "v": 2,
    "key": {
      "email": 1
    },
    "name": "email_1",
    "unique": true
  }
]
```

#### Creating an Index

**Query**: `mongo-llm run "create an index on the age field in users collection"`

**Output**:
```
age_1
```

#### Dropping an Index

**Query**: `mongo-llm run "drop the index named age_1 from users collection"`

**Output**:
```
This operation will remove an index from a collection. 
Are you sure you want to drop_index on collection 'users' with index_name=age_1? [y/N]: y
Operation completed successfully with no data.
```

## Best Practices

1. **Be Specific**: The more specific your query, the better the LLM can understand your intent.

2. **Confirm Destructive Operations**: Always double-check before confirming destructive operations like delete or drop.

3. **Check Collection Names**: Make sure to use the correct collection names in your queries.

4. **Use Limits**: When retrieving documents, consider adding a limit to avoid retrieving too many documents.

5. **Query Parameters**: For complex queries, be explicit about fields and conditions.

## Troubleshooting

### Connection Issues

If you see a connection error:

1. Verify your MongoDB URI in the `.env` file
2. Ensure your MongoDB server is running
3. Check network connectivity and firewall settings

### LLM Parsing Issues

If the LLM misunderstands your query:

1. Try rephrasing the query to be more specific
2. Include field names and explicit conditions
3. Break complex queries into simpler ones

### Permission Issues

If you encounter permission errors:

1. Ensure your MongoDB user has the necessary permissions
2. Check database and collection access rights 