from pymongo import MongoClient
from typing import Any, Dict, List
from base import DatabaseAdapter


class MongoAdapter(DatabaseAdapter):
    def __init__(self, db_url: str):
        self.client = MongoClient(db_url)
        self.db = self.client.get_default_database()

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

    def validate_query(self, query: Dict[str, Any]):
        if "drop" in query:
            raise ValueError("Drop not allowed")

    def execute_query(self, query: Dict[str, Any], *, params=None, limit=None):
        self.validate_query(query)
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
