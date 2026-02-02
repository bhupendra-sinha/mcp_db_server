from adapters.base import create_adapter
from cli import parse_args
from server import create_server


def main():
    args = parse_args()

    adapter = create_adapter(args.db_type, args.db_url)

    mcp = create_server(adapter)

    # 🚀 THIS ACTUALLY STARTS THE MCP SERVER
    mcp.run()


if __name__ == "__main__":
    main()
