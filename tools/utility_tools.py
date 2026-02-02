def register_utility_tools(mcp, adapter):

    @mcp.tool(
        name="get_raw_client",
        description=(
            "Return the underlying database client. "
            "Use only for advanced or unsupported operations."
        )
    )
    def get_raw_client():
        return str(adapter.raw_client())
