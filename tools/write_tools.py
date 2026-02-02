from typing import Dict, Any, List


def register_write_tools(mcp, adapter):

    @mcp.tool(
        name="insert_row",
        description="Insert a single row or document into a table or collection. Provide table name and data as a dictionary."
    )
    def insert_row(table: str, data: Dict[str, Any]):
        try:
            adapter.insert(table, data)
            return f"Successfully inserted 1 row into {table}"
        except Exception as e:
            return f"Error inserting into {table}: {str(e)}"

    @mcp.tool(
        name="bulk_insert",
        description="Insert multiple rows or documents. Provide table name and list of data dictionaries."
    )
    def bulk_insert(table: str, data: List[Dict[str, Any]]):
        try:
            adapter.bulk_insert(table, data)
            return f"Successfully inserted {len(data)} rows into {table}"
        except Exception as e:
            return f"Error bulk inserting into {table}: {str(e)}"

    @mcp.tool(
        name="update_rows",
        description="Update rows or documents matching filters. Provide table name, filters dict, and data dict to update."
    )
    def update_rows(
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ):
        try:
            adapter.update(table, filters, data)
            return f"Successfully updated rows in {table} matching filters: {filters}"
        except Exception as e:
            return f"Error updating {table}: {str(e)}"

    @mcp.tool(
        name="delete_rows",
        description="Delete rows or documents matching filters. Provide table name and filters dict."
    )
    def delete_rows(
        table: str,
        filters: Dict[str, Any],
    ):
        try:
            adapter.delete(table, filters)
            return f"Successfully deleted rows from {table} matching filters: {filters}"
        except Exception as e:
            return f"Error deleting from {table}: {str(e)}"
