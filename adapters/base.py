from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class DatabaseAdapter(ABC):
    """
    Abstract base class for all database adapters.
    This contract is intentionally rich to support:
    - SQL / NoSQL / Vector DBs
    - MCP agent tool selection
    - Production observability
    """

    # -------------------------
    # 🔌 Connection lifecycle
    # -------------------------

    @abstractmethod
    def connect(self) -> None:
        """Initialize DB connection / client."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Gracefully close DB connections."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if database is reachable."""
        pass

    # -------------------------
    # 🧠 Capability discovery (Agent uses this!)
    # -------------------------

    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """
        Example:
        {
            "read": True,
            "write": False,
            "transactions": True,
            "schema_introspection": True,
            "aggregation": True
        }
        """
        pass

    # -------------------------
    # 📐 Schema & metadata
    # -------------------------

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return tables / collections & fields."""
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """List tables or collections."""
        pass

    @abstractmethod
    def get_columns(self, table: str) -> List[str]:
        """List columns / fields for a table."""
        pass

    @abstractmethod
    def get_indexes(self, table: str) -> Any:
        """Return indexes for a table / collection."""
        pass

    # -------------------------
    # 🔍 Query execution
    # -------------------------

    @abstractmethod
    def execute_query(
        self,
        query: Union[str, Dict[str, Any]],
        *,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a READ query.
        SQL → string
        Mongo → dict
        """
        pass

    @abstractmethod
    def explain_query(self, query: Union[str, Dict[str, Any]]) -> Any:
        """Return query execution plan."""
        pass

    # -------------------------
    # ✍️ Controlled writes (optional but production-ready)
    # -------------------------

    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def bulk_insert(self, table: str, data: List[Dict[str, Any]]) -> Any:
        pass

    @abstractmethod
    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Any:
        pass

    @abstractmethod
    def delete(self, table: str, filters: Dict[str, Any]) -> Any:
        pass

    # -------------------------
    # 🔄 Transactions
    # -------------------------

    @abstractmethod
    def begin_transaction(self) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    # -------------------------
    # 📊 Aggregations & analytics
    # -------------------------

    @abstractmethod
    def aggregate(
        self,
        table: str,
        pipeline: Any,
    ) -> Any:
        """SQL GROUP BY / Mongo pipeline."""
        pass

    # -------------------------
    # 🧾 Pagination & streaming
    # -------------------------

    @abstractmethod
    def fetch_many(
        self,
        query: Union[str, Dict[str, Any]],
        batch_size: int = 1000,
    ):
        """Generator for large result sets."""
        pass

    # -------------------------
    # 🔐 Security & validation
    # -------------------------

    @abstractmethod
    def validate_query(self, query: Union[str, Dict[str, Any]]) -> None:
        """Prevent unsafe operations."""
        pass

    # -------------------------
    # 🧩 Utilities
    # -------------------------

    @abstractmethod
    def raw_client(self) -> Any:
        """Expose underlying DB client (escape hatch)."""
        pass


def create_adapter(db_type: str, db_url: str):
    if db_type == "postgresql" or db_type == "postgres":
        from adapters.postgresql_adapter import PostgresAdapter
        adapter = PostgresAdapter(db_url)
    elif db_type == "mysql":
        from adapters.mysql_adapter import MySQLAdapter
        adapter = MySQLAdapter(db_url)
    elif db_type == "mongodb" or db_type == "mongo":
        from adapters.mongo_adapter import MongoAdapter
        adapter = MongoAdapter(db_url)
    elif db_type == "sqlite":
        from adapters.sqlite_adapter import SQLiteAdapter
        adapter = SQLiteAdapter(db_url)
    else:
        raise ValueError(f"Unsupported db type: {db_type}")

    adapter.connect()
    return adapter