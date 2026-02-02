from typing import Any


def register_aggregation_tools(mcp, adapter):

    @mcp.tool(
        name="aggregate_data",
        description=(
            "Run aggregation queries. "
            "SQL: GROUP BY / aggregate query. "
            "MongoDB: aggregation pipeline."
        )
    )
    def aggregate_data(
        table: str,
        pipeline: Any,
    ):
        return adapter.aggregate(table, pipeline)
