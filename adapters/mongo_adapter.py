from pymongo import MongoClient
from typing import Any, Dict, List
from adapters.base import DatabaseAdapter
from urllib.parse import quote_plus, urlparse, urlunparse
import re


class MongoAdapter(DatabaseAdapter):
    def __init__(self, db_url: str):
        # Auto-encode credentials if they contain special characters
        db_url = self._encode_mongodb_uri(db_url)
        self.client = MongoClient(db_url)
        
        # Try to get default database, fallback to listing available databases
        try:
            self.db = self.client.get_default_database()
        except Exception:
            # No default database specified in URI, use the first available database
            # or create a 'default' database
            db_names = self.client.list_database_names()
            # Filter out system databases
            user_dbs = [db for db in db_names if db not in ['admin', 'local', 'config']]
            if user_dbs:
                self.db = self.client[user_dbs[0]]
            else:
                # Use 'test' as default database if none exist
                self.db = self.client['test']

    def _encode_mongodb_uri(self, uri: str) -> str:
        """
        Automatically encode username and password in MongoDB URI if they contain special characters.
        """
        # Check if URI has the pattern mongodb://... or mongodb+srv://...
        if not uri.startswith(('mongodb://', 'mongodb+srv://')):
            return uri
        
        # Extract scheme
        if uri.startswith('mongodb+srv://'):
            scheme = 'mongodb+srv://'
            rest = uri[14:]  # Remove 'mongodb+srv://'
        else:
            scheme = 'mongodb://'
            rest = uri[10:]  # Remove 'mongodb://'
        
        # Find the last @ which separates credentials from host
        last_at = rest.rfind('@')
        if last_at == -1:
            # No credentials in URI
            return uri
        
        credentials = rest[:last_at]
        host_part = rest[last_at + 1:]
        
        # Split credentials into username and password
        colon_pos = credentials.find(':')
        if colon_pos == -1:
            # No password, only username
            return uri
        
        username = credentials[:colon_pos]
        password = credentials[colon_pos + 1:]
        
        # Check if credentials need encoding (contain special chars)
        needs_encoding = any(char in username + password for char in ['@', ':', '/', '?', '#', '[', ']', '!', '$', '&', "'", '(', ')', '*', '+', ',', ';', '='])
        
        if needs_encoding:
            # Encode username and password
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            return f"{scheme}{encoded_username}:{encoded_password}@{host_part}"
        
        return uri

    # ---------------- Connection ----------------

    def connect(self):
        self.client.admin.command("ping")

    def close(self):
        self.client.close()

    def health_check(self) -> bool:
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    # ---------------- Capabilities ----------------

    def capabilities(self):
        return {
            "read": True,
            "write": True,
            "transactions": False,
            "schema_introspection": False,
            "aggregation": True,
        }

    # ---------------- Schema ----------------

    def get_schema(self):
        return {c: {} for c in self.db.list_collection_names()}

    def get_tables(self):
        return self.db.list_collection_names()

    def get_columns(self, table: str):
        sample = self.db[table].find_one()
        return list(sample.keys()) if sample else []

    def get_indexes(self, table: str):
        return self.db[table].index_information()

    # ---------------- Query ----------------

    def validate_query(self, query: Any):
        if isinstance(query, dict) and "drop" in query:
            raise ValueError("Drop not allowed")
        if isinstance(query, str) and "drop" in query.lower():
            raise ValueError("Drop not allowed")

    def execute_query(self, query: Any, *, params=None, limit=None):
        self.validate_query(query)
        
        # Handle string queries (SQL or natural language)
        if isinstance(query, str):
            # MongoDB doesn't support SQL - return helpful error
            if any(keyword in query.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE']):
                raise ValueError(
                    "MongoDB doesn't support SQL queries. Please use MongoDB query syntax or natural language. "
                    "Example: To list all documents, use: {'collection': 'your_collection', 'filter': {}}"
                )
            else:
                raise ValueError(
                    "Please specify MongoDB query as a dictionary with 'collection' and optional 'filter' keys. "
                    f"Example: {{'collection': 'users', 'filter': {{'age': {{'$gt': 18}}}}}}"
                )
        
        # Handle dictionary queries (MongoDB native)
        if not isinstance(query, dict):
            raise ValueError("Query must be a string or dictionary")
            
        if "collection" not in query:
            raise ValueError("Query dictionary must include 'collection' key")
        
        collection = self.db[query["collection"]]
        cursor = collection.find(query.get("filter", {}))
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def explain_query(self, query):
        collection = self.db[query["collection"]]
        return collection.find(query.get("filter", {})).explain()

    # ---------------- Writes ----------------

    def insert(self, table: str, data: Dict[str, Any]):
        return self.db[table].insert_one(data).inserted_id

    def bulk_insert(self, table: str, data: List[Dict[str, Any]]):
        return self.db[table].insert_many(data).inserted_ids

    def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]):
        return self.db[table].update_many(filters, {"$set": data})

    def delete(self, table: str, filters: Dict[str, Any]):
        return self.db[table].delete_many(filters)

    # ---------------- Aggregation ----------------

    def aggregate(self, table: str, pipeline: List[Dict[str, Any]]):
        return list(self.db[table].aggregate(pipeline))

    # ---------------- Streaming ----------------

    def fetch_many(self, query: Dict[str, Any], batch_size: int = 1000):
        cursor = self.db[query["collection"]].find(
            query.get("filter", {})
        ).batch_size(batch_size)
        for doc in cursor:
            yield doc

    def raw_client(self):
        return self.client

    # ---------------- Transactions ----------------

    def begin_transaction(self):
        # MongoDB transactions require replica sets
        # For simplicity, we'll use a no-op implementation
        pass

    def commit(self):
        # MongoDB transactions require replica sets
        pass

    def rollback(self):
        # MongoDB transactions require replica sets
        pass
