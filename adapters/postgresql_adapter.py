from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from typing import Any, Dict, List
from adapters.base import DatabaseAdapter
from security.validator import validate_sql


class PostgresAdapter(DatabaseAdapter):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine: Engine | None = None

    # ---------------- Connection ----------------

    def connect(self) -> None:
        self.engine = create_engine(
            self.db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )

    def close(self) -> None:
        if self.engine:
            self.engine.dispose()

    def health_check(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    # ---------------- Capabilities ----------------

    def capabilities(self) -> Dict[str, bool]:
        return {
            "read": True,
            "write": True,
            "transactions": True,
            "schema_introspection": True,
            "aggregation": True,
        }

    # ---------------- Schema ----------------

    def get_schema(self) -> Dict[str, Any]:
        inspector = inspect(self.engine)
        schema = {}
        for table in inspector.get_table_names():
            schema[table] = self.get_columns(table)
        return schema

    def get_tables(self) -> List[str]:
        return inspect(self.engine).get_table_names()

    def get_columns(self, table: str) -> List[str]:
        inspector = inspect(self.engine)
        return [c["name"] for c in inspector.get_columns(table)]

    def get_indexes(self, table: str) -> Any:
        return inspect(self.engine).get_indexes(table)

    # ---------------- Query ----------------

    def validate_query(self, query: str) -> None:
        validate_sql(query, allow_dml=False)

    def execute_query(self, query: str, *, params=None, limit=None):
        self.validate_query(query)

        if limit:
            query = f"{query} LIMIT {limit}"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    def explain_query(self, query: str):
        with self.engine.connect() as conn:
            return conn.execute(text(f"EXPLAIN {query}")).fetchall()

    # ---------------- Transactions ----------------

    def begin_transaction(self):
        self._tx = self.engine.begin()

    def commit(self):
        self._tx.commit()

    def rollback(self):
        self._tx.rollback()

    # ---------------- Writes ----------------

    def insert(self, table: str, data: Dict[str, Any]):
        keys = ", ".join(data.keys())
        values = ", ".join([f":{k}" for k in data])
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        with self.engine.begin() as conn:
            conn.execute(text(query), data)

    def bulk_insert(self, table: str, data: List[Dict[str, Any]]):
        if not data:
            return
        self.insert(table, data[0])  # SQLAlchemy auto-optimizes bulk

    def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]):
        set_clause = ", ".join([f"{k}=:{k}" for k in data])
        where = " AND ".join([f"{k}=:_f_{k}" for k in filters])

        params = data | {f"_f_{k}": v for k, v in filters.items()}

        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        with self.engine.begin() as conn:
            conn.execute(text(query), params)

    def delete(self, table: str, filters: Dict[str, Any]):
        where = " AND ".join([f"{k}=:{k}" for k in filters])
        query = f"DELETE FROM {table} WHERE {where}"
        with self.engine.begin() as conn:
            conn.execute(text(query), filters)

    # ---------------- Aggregation ----------------

    def aggregate(self, table: str, pipeline: str):
        return self.execute_query(pipeline)

    # ---------------- Streaming ----------------

    def fetch_many(self, query: str, batch_size: int = 1000):
        self.validate_query(query)
        with self.engine.connect() as conn:
            result = conn.execution_options(stream_results=True).execute(text(query))
            while True:
                rows = result.fetchmany(batch_size)
                if not rows:
                    break
                yield [dict(r._mapping) for r in rows]

    def raw_client(self):
        return self.engine
