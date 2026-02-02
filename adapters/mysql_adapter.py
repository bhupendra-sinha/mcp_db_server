from adapters.postgresql_adapter import PostgresAdapter
from sqlalchemy import text


class MySQLAdapter(PostgresAdapter):
    """
    MySQL adapter with MySQL-specific overrides.
    DB URL example:
    mysql+pymysql://user:password@host:3306/database
    """
    
    def explain_query(self, query: str):
        """MySQL uses EXPLAIN differently than PostgreSQL"""
        with self.engine.connect() as conn:
            # MySQL EXPLAIN returns different format
            result = conn.execute(text(f"EXPLAIN {query}"))
            return [dict(row._mapping) for row in result]
    
    def get_indexes(self, table: str):
        """MySQL has different index information structure"""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SHOW INDEX FROM {table}"))
            return [dict(row._mapping) for row in result]
    
    def health_check(self) -> bool:
        """MySQL-specific health check"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
