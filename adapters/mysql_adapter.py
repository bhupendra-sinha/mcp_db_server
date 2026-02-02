
from adapters.postgresql_adapter import PostgresAdapter


class MySQLAdapter(PostgresAdapter):
    """
    MySQL adapter reuses SQL logic.
    DB URL example:
    mysql+pymysql://user:password@host/db
    """
    pass
