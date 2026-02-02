def register_transaction_tools(mcp, adapter):

    @mcp.tool(
        name="begin_transaction",
        description="Begin a database transaction"
    )
    def begin_transaction():
        adapter.begin_transaction()
        return {"status": "transaction_started"}

    @mcp.tool(
        name="commit_transaction",
        description="Commit the current transaction"
    )
    def commit_transaction():
        adapter.commit()
        return {"status": "transaction_committed"}

    @mcp.tool(
        name="rollback_transaction",
        description="Rollback the current transaction"
    )
    def rollback_transaction():
        adapter.rollback()
        return {"status": "transaction_rolled_back"}
