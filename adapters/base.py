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

    @abstractmethod
    def begin_transaction(self) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def aggregate(
        self,
        table: str,
        pipeline: Any,
    ) -> Any:
        """SQL GROUP BY / Mongo pipeline."""
        pass

    @abstractmethod
    def fetch_many(
        self,
        query: Union[str, Dict[str, Any]],
        batch_size: int = 1000,
    ):
        """Generator for large result sets."""
        pass

    @abstractmethod
    def validate_query(self, query: Union[str, Dict[str, Any]]) -> None:
        """Prevent unsafe operations."""
        pass

    @abstractmethod
    def raw_client(self) -> Any:
        """Expose underlying DB client (escape hatch)."""
        pass


def create_adapter(db_type: str, db_url: str):
    # Validate that connection string matches database type
    db_url_lower = db_url.lower()
    
    if db_type == "postgresql" or db_type == "postgres":
        if not (db_url_lower.startswith("postgresql://") or db_url_lower.startswith("postgres://")):
            raise ValueError(
                f"Invalid connection string for PostgreSQL. "
                f"Expected format: postgresql://user:password@host:5432/database"
            )
        from adapters.postgresql_adapter import PostgresAdapter
        adapter = PostgresAdapter(db_url)
    elif db_type == "mysql":
        if not db_url_lower.startswith("mysql"):
            raise ValueError(
                f"Invalid connection string for MySQL. "
                f"Expected format: mysql+pymysql://user:password@host:3306/database"
            )
        from adapters.mysql_adapter import MySQLAdapter
        adapter = MySQLAdapter(db_url)
    elif db_type == "mongodb" or db_type == "mongo":
        if not db_url_lower.startswith("mongodb"):
            raise ValueError(
                f"Invalid connection string for MongoDB. "
                f"Expected format: mongodb://user:password@host:27017/database or mongodb+srv://..."
            )
        from adapters.mongo_adapter import MongoAdapter
        adapter = MongoAdapter(db_url)
    elif db_type == "sqlite":
        if not db_url_lower.startswith("sqlite://"):
            raise ValueError(
                f"Invalid connection string for SQLite. "
                f"Expected format: sqlite:///path/to/database.db"
            )
        from adapters.sqlite_adapter import SQLiteAdapter
        adapter = SQLiteAdapter(db_url)
    else:
        raise ValueError(f"Unsupported db type: {db_type}")

    adapter.connect()
    return adapter