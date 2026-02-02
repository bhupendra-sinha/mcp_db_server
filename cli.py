import argparse

def parse_args():
    parser = argparse.ArgumentParser("mcp-db-server")

    parser.add_argument(
        "--db-url",
        required=True,
        help="Database connection string"
    )

    parser.add_argument(
        "--db-type",
        required=True,
        choices=["postgres", "mysql", "sqlite", "mongo"],
        help="Database type"
    )

    return parser.parse_args()
