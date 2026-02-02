from fastmcp import FastMCP
from tools.system_tools import register_system_tools
from tools.schema_tools import register_schema_tools
from tools.query_tools import register_query_tools
from tools.aggregation_tools import register_aggregation_tools
from tools.pagination_tools import register_pagination_tools
from tools.write_tools import register_write_tools
from tools.transaction_tools import register_transaction_tools
from tools.utility_tools import register_utility_tools


def create_server(adapter):
    mcp = FastMCP("mcp-db-server")

    register_system_tools(mcp, adapter)
    register_schema_tools(mcp, adapter)
    register_query_tools(mcp, adapter)
    register_aggregation_tools(mcp, adapter)
    register_pagination_tools(mcp, adapter)
    register_write_tools(mcp, adapter)
    register_transaction_tools(mcp, adapter)
    register_utility_tools(mcp, adapter)

    return mcp
