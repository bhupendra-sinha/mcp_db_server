
from adapters.postgresql_adapter import PostgresAdapter


class SQLiteAdapter(PostgresAdapter):
    """
    SQLite adapter for local / embedded DBs.
    DB URL example:
    sqlite:///./app.db
    """
    pass
