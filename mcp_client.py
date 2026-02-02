import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(override=True)

# MODEL_NAME = "gpt-5-mini-2025-08-07"
MODEL_NAME = "gpt-5.2-2025-12-11"


class MCPClient:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions: list[ClientSession] = []

        self.llm = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    async def connect_to_server(self, server_script_path: str, server_args: list = None):
        """Connect to ONE MCP server (file-based)"""
        if not server_script_path.endswith((".py", ".js")):
            raise ValueError("Server script must be a .py or .js file")

        if server_script_path.endswith(".py"):
            path = Path(server_script_path).resolve()
            args_list = [str(path)]
            if server_args:
                args_list.extend(server_args)
            
            server_params = StdioServerParameters(
                command=sys.executable,
                args=args_list,
                env=None,
            )
        else:
            args_list = [server_script_path]
            if server_args:
                args_list.extend(server_args)
            
            server_params = StdioServerParameters(
                command="node",
                args=args_list,
                env=None,
            )

        stdio, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        await session.initialize()
        self.sessions.append(session)

        tools = (await session.list_tools()).tools
        print(f"✓ Connected to {Path(server_script_path).name} → {[t.name for t in tools]}")

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        # 🔑 Collect tools from ALL servers
        tool_map = {}
        tools_for_llm = []

        for session in self.sessions:
            resp = await session.list_tools()
            for tool in resp.tools:
                tool_map[tool.name] = session
                tools_for_llm.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                )

        response = await self.llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools_for_llm,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            for call in msg.tool_calls:
                tool_name = call.function.name
                tool_args = call.function.arguments

                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)

                session = tool_map[tool_name]
                result = await session.call_tool(tool_name, tool_args)

                messages.append(msg)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result.content,
                    }
                )

                followup = await self.llm.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                )

                return followup.choices[0].message.content

        return msg.content

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break

            try:
                response = await self.process_query(query)
                print("\n" + str(response))
            except Exception as e:
                print("\nError:", e)

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <server.py> [server arguments...]")
        print("\nExamples:")
        print("  python mcp_client.py universal_db_server.py -c 'postgresql://...'")
        print("  python mcp_client.py weather_server.py")
        sys.exit(1)
    
    # First argument is the server script
    server_script = sys.argv[1]
    
    # All remaining arguments are passed to the server
    server_args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    client = MCPClient()
    try:
        # Connect to server with all arguments forwarded
        await client.connect_to_server(server_script, server_args)
        
        print(f"\n🚀 Connected to {len(client.sessions)} server(s)")
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
