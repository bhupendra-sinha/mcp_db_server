import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Optional
from fastapi import HTTPException
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv



load_dotenv(override=True)

# MODEL_NAME = "gpt-4o-mini"
MODEL_NAME = os.getenv("MODEL_NAME")

class MCPClientManager:
    def __init__(self):
        self.exit_stack: Optional[AsyncExitStack] = None
        self.session: Optional[ClientSession] = None
        self.llm = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.connected = False

    async def connect(self, db_type: str, db_url: str):
        if self.connected:
            await self.disconnect()

        # Map frontend db_type to CLI db_type
        db_type_mapping = {
            "mongo": "mongo",
            "postgres": "postgres",
            "postgresql": "postgres",
            "mysql": "mysql",
            "sqlite": "sqlite"
        }
        
        mapped_db_type = db_type_mapping.get(db_type.lower(), db_type)

        self.exit_stack = AsyncExitStack()
        
        try:
            # server_script = str(Path(__file__).parent / "main.py")
            # server_args = ["--db-type", mapped_db_type, "--db-url", db_url]
            
            # args_list = [server_script] + server_args
            
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["-m","mcp_server","--db-type", mapped_db_type, "--db-url", db_url],
                env=None,
            )

            stdio, write = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )

            await self.session.initialize()
            self.connected = True
            
            tools = (await self.session.list_tools()).tools
            return {"status": "connected", "tools": [t.name for t in tools]}
        except Exception as e:
            # Clean up on connection failure
            if self.exit_stack:
                try:
                    await self.exit_stack.aclose()
                except:
                    pass
                self.exit_stack = None
            self.session = None
            self.connected = False
            raise Exception(f"Failed to connect to database: {str(e)}")

    async def disconnect(self):
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                # Ignore cleanup errors during disconnect
                print(f"Warning: Error during disconnect cleanup: {e}")
            finally:
                self.exit_stack = None
                self.session = None
                self.connected = False

    # async def process_query(self, query: str):
    #     if not self.connected or not self.session:
    #         raise HTTPException(status_code=400, detail="Not connected to database")

    #     system_prompt = """You are a database assistant with access to database tools. 

    #                 IMPORTANT INSTRUCTIONS:
    #                 - When the user provides SQL INSERT/UPDATE/DELETE statements, parse them and use the appropriate tools (insert_row, update_rows, delete_rows)
    #                 - When the user asks to insert data, use the insert_row or bulk_insert tool
    #                 - When the user asks to update data, use the update_rows tool
    #                 - When the user asks to delete data, use the delete_rows tool
    #                 - For SQL databases: When the user asks to query/select data, use the execute_query tool with SQL string
    #                 - For MongoDB: Use execute_query with a dictionary format: {'collection': 'name', 'filter': {...}}
    #                 - For listing tables/collections, use the list_tables tool
    #                 - For schema information, use get_table_columns or get_database_schema tools

    #                 MONGODB SPECIFIC:
    #                 - MongoDB uses collections (not tables) and documents (not rows)
    #                 - For queries, use MongoDB query syntax with filters like: {'field': 'value'} or {'field': {'$gt': 10}}
    #                 - Do NOT use SQL syntax for MongoDB queries

    #                 Always use the tools available to you. Do not just explain what the query does - actually execute it using the appropriate tool."""

    #     messages = [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": query}
    #     ]

    #     tool_map = {}
    #     tools_for_llm = []

    #     resp = await self.session.list_tools()
    #     for tool in resp.tools:
    #         tool_map[tool.name] = self.session
    #         tools_for_llm.append(
    #             {
    #                 "type": "function",
    #                 "function": {
    #                     "name": tool.name,
    #                     "description": tool.description,
    #                     "parameters": tool.inputSchema,
    #                 },
    #             }
    #         )

    #     response = await self.llm.chat.completions.create(
    #         model=MODEL_NAME,
    #         messages=messages,
    #         tools=tools_for_llm,
    #         tool_choice="auto",
    #     )

    #     msg = response.choices[0].message

    #     if msg.tool_calls:
    #         messages.append(msg)
            
    #         for call in msg.tool_calls:
    #             tool_name = call.function.name
    #             tool_args = call.function.arguments

    #             if isinstance(tool_args, str):
    #                 tool_args = json.loads(tool_args)

    #             result = await self.session.call_tool(tool_name, tool_args)

    #             content_str = ""
    #             if isinstance(result.content, list):
    #                 for item in result.content:
    #                     if hasattr(item, 'text'):
    #                         content_str += item.text
    #                     else:
    #                         content_str += str(item)
    #             elif isinstance(result.content, str):
    #                 content_str = result.content
    #             else:
    #                 content_str = str(result.content)

    #             messages.append(
    #                 {
    #                     "role": "tool",
    #                     "tool_call_id": call.id,
    #                     "content": content_str,
    #                 }
    #             )

    #         followup = await self.llm.chat.completions.create(
    #             model=MODEL_NAME,
    #             messages=messages,
    #         )

    #         response_content = followup.choices[0].message.content
            
    #         try:
    #             parsed = json.loads(response_content)
    #             return {"response": response_content, "data": parsed}
    #         except:
    #             return {"response": response_content}

    #     return {"response": msg.content}

    async def process_query_stream(self, query: str):
        if not self.connected or not self.session:
            raise HTTPException(status_code=400, detail="Not connected to database")

        system_prompt = """You are a database assistant with access to database tools.
                        Always use tools when required."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        # Prepare tools
        tool_map = {}
        tools_for_llm = []

        resp = await self.session.list_tools()
        for tool in resp.tools:
            tool_map[tool.name] = self.session
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

        # STEP 1: Stream first LLM response (may contain tool calls)
        stream = await self.llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools_for_llm,
            tool_choice="auto",
            stream=True,
        )

        tool_calls = {}
        assistant_content = ""

        async for chunk in stream:
            delta = chunk.choices[0].delta

            # If content token
            if delta.content:
                assistant_content += delta.content
                yield f"data: {delta.content}\n\n"

            # If tool call streaming
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    idx = tool_call.index
                    if idx not in tool_calls:
                        tool_calls[idx] = {
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": ""
                        }

                    if tool_call.function.arguments:
                        tool_calls[idx]["arguments"] += tool_call.function.arguments

        # If no tool calls → done
        if not tool_calls:
            yield "data: [DONE]\n\n"
            return

        # STEP 2: Execute Tools
        messages.append({
            "role": "assistant",
            "content": assistant_content,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"]
                    }
                }
                for tc in tool_calls.values()
            ]
        })

        for tc in tool_calls.values():
            tool_args = json.loads(tc["arguments"])
            result = await self.session.call_tool(tc["name"], tool_args)

            content_str = ""
            if isinstance(result.content, list):
                for item in result.content:
                    if hasattr(item, "text"):
                        content_str += item.text
                    else:
                        content_str += str(item)
            else:
                content_str = str(result.content)

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": content_str
            })

        # STEP 3: Stream final answer
        final_stream = await self.llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
        )

        async for chunk in final_stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield f"data: {delta.content}\n\n"

        yield "data: [DONE]\n\n"


# client_manager = MCPClientManager()