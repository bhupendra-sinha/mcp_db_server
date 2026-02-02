from adapters.postgresql_adapter import PostgresAdapter
from sqlalchemy import text, create_engine


class SQLiteAdapter(PostgresAdapter):
    """
    SQLite adapter for local / embedded DBs.
    DB URL example:
    sqlite:///./app.db or sqlite:////absolute/path/to/database.db
    """
    
    def connect(self) -> None:
        """SQLite-specific connection without pooling (not needed for file-based DB)"""
        self.engine = create_engine(
            self.db_url,
            connect_args={"check_same_thread": False},  # Allow multi-threaded access
            pool_pre_ping=True,
        )
    
    def capabilities(self):
        """SQLite has limited transaction support and no advanced features"""
        return {
            "read": True,
            "write": True,
            "transactions": True,  # Basic transactions supported
            "schema_introspection": True,
            "aggregation": True,
        }
    
    def explain_query(self, query: str):
        """SQLite uses EXPLAIN QUERY PLAN"""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"EXPLAIN QUERY PLAN {query}"))
            return [dict(row._mapping) for row in result]
    
    def get_indexes(self, table: str):
        """SQLite-specific index query"""
        with self.engine.connect() as conn:
            # Get index list
            result = conn.execute(text(f"PRAGMA index_list('{table}')"))
            indexes = []
            for row in result:
                index_name = row[1]  # index name is second column
                # Get index info
                info_result = conn.execute(text(f"PRAGMA index_info('{index_name}')"))
                indexes.append({
                    'name': index_name,
                    'columns': [info_row[2] for info_row in info_result]  # column name is third column
                })
            return indexes
    
    def begin_transaction(self):
        """SQLite transaction handling"""
        self._tx = self.engine.begin()
    
    def commit(self):
        """Commit SQLite transaction"""
        if hasattr(self, '_tx'):
            self._tx.commit()
    
    def rollback(self):
        """Rollback SQLite transaction"""
        if hasattr(self, '_tx'):
            self._tx.rollback()
