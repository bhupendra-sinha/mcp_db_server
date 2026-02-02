from mcp.server.fastmcp import FastMCP


def register_system_tools(mcp: FastMCP, adapter):

    @mcp.tool(
        name="health_check",
        description="Check whether the database is reachable and healthy"
    )
    def health_check() -> bool:
        return adapter.health_check()

    @mcp.tool(
        name="get_capabilities",
        description="Return database capabilities such as read, write, transactions, aggregation"
    )
    def get_capabilities() -> dict:
        return adapter.capabilities()
