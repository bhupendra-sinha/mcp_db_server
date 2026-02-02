from typing import Optional, Dict, Any, Union


def register_query_tools(mcp, adapter):

    @mcp.tool(
        name="execute_query",
        description=(
            "Execute a READ query on the database. "
            "SQL databases accept SQL strings. "
            "MongoDB accepts structured query objects."
        )
    )
    def execute_query(
        query: Union[str, Dict[str, Any]],
        limit: Optional[int] = None,
    ):
        return adapter.execute_query(query, limit=limit)

    @mcp.tool(
        name="explain_query",
        description="Explain query execution plan and estimated cost"
    )
    def explain_query(query: Union[str, Dict[str, Any]]):
        return adapter.explain_query(query)
