from typing import Dict, Any, List


def register_write_tools(mcp, adapter):

    @mcp.tool(
        name="insert_row",
        description="Insert a single row or document into a table or collection"
    )
    def insert_row(table: str, data: Dict[str, Any]):
        return adapter.insert(table, data)

    @mcp.tool(
        name="bulk_insert",
        description="Insert multiple rows or documents"
    )
    def bulk_insert(table: str, data: List[Dict[str, Any]]):
        return adapter.bulk_insert(table, data)

    @mcp.tool(
        name="update_rows",
        description="Update rows or documents matching filters"
    )
    def update_rows(
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ):
        return adapter.update(table, filters, data)

    @mcp.tool(
        name="delete_rows",
        description="Delete rows or documents matching filters"
    )
    def delete_rows(
        table: str,
        filters: Dict[str, Any],
    ):
        return adapter.delete(table, filters)
