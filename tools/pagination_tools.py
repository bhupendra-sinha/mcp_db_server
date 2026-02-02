from typing import Any, Dict, Union


def register_pagination_tools(mcp, adapter):

    @mcp.tool(
        name="fetch_large_result",
        description=(
            "Fetch large query results in batches to avoid memory issues. "
            "Returns data incrementally."
        )
    )
    def fetch_large_result(
        query: Union[str, Dict[str, Any]],
        batch_size: int = 1000,
    ):
        results = []
        for batch in adapter.fetch_many(query, batch_size=batch_size):
            results.extend(batch)
        return results
