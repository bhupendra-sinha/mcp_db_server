def register_schema_tools(mcp, adapter):

    @mcp.tool(
        name="get_database_schema",
        description="Get full database schema (tables/collections and fields)"
    )
    def get_database_schema():
        return adapter.get_schema()

    @mcp.tool(
        name="list_tables",
        description="List all tables or collections in the database"
    )
    def list_tables():
        return adapter.get_tables()

    @mcp.tool(
        name="get_table_columns",
        description="Get columns or fields for a specific table or collection"
    )
    def get_table_columns(table: str):
        return adapter.get_columns(table)

    @mcp.tool(
        name="get_table_indexes",
        description="Get indexes for a table or collection"
    )
    def get_table_indexes(table: str):
        return adapter.get_indexes(table)
