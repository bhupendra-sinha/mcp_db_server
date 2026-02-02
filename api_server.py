import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(override=True)

app = FastAPI(title="MCP Database API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "gpt-4o-mini"


class QueryRequest(BaseModel):
    query: str


class ConnectRequest(BaseModel):
    db_type: str
    db_url: str


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
            server_script = str(Path(__file__).parent / "main.py")
            server_args = ["--db-type", mapped_db_type, "--db-url", db_url]
            
            args_list = [server_script] + server_args
            
            server_params = StdioServerParameters(
                command=sys.executable,
                args=args_list,
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

    async def process_query(self, query: str):
        if not self.connected or not self.session:
            raise HTTPException(status_code=400, detail="Not connected to database")

        system_prompt = """You are a database assistant with access to database tools. 

IMPORTANT INSTRUCTIONS:
- When the user provides SQL INSERT/UPDATE/DELETE statements, parse them and use the appropriate tools (insert_row, update_rows, delete_rows)
- When the user asks to insert data, use the insert_row or bulk_insert tool
- When the user asks to update data, use the update_rows tool
- When the user asks to delete data, use the delete_rows tool
- For SQL databases: When the user asks to query/select data, use the execute_query tool with SQL string
- For MongoDB: Use execute_query with a dictionary format: {'collection': 'name', 'filter': {...}}
- For listing tables/collections, use the list_tables tool
- For schema information, use get_table_columns or get_database_schema tools

MONGODB SPECIFIC:
- MongoDB uses collections (not tables) and documents (not rows)
- For queries, use MongoDB query syntax with filters like: {'field': 'value'} or {'field': {'$gt': 10}}
- Do NOT use SQL syntax for MongoDB queries

Always use the tools available to you. Do not just explain what the query does - actually execute it using the appropriate tool."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

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

        response = await self.llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools_for_llm,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            
            for call in msg.tool_calls:
                tool_name = call.function.name
                tool_args = call.function.arguments

                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)

                result = await self.session.call_tool(tool_name, tool_args)

                content_str = ""
                if isinstance(result.content, list):
                    for item in result.content:
                        if hasattr(item, 'text'):
                            content_str += item.text
                        else:
                            content_str += str(item)
                elif isinstance(result.content, str):
                    content_str = result.content
                else:
                    content_str = str(result.content)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": content_str,
                    }
                )

            followup = await self.llm.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
            )

            response_content = followup.choices[0].message.content
            
            try:
                parsed = json.loads(response_content)
                return {"response": response_content, "data": parsed}
            except:
                return {"response": response_content}

        return {"response": msg.content}


client_manager = MCPClientManager()


@app.on_event("shutdown")
async def shutdown_event():
    await client_manager.disconnect()


@app.post("/api/connect")
async def connect(request: ConnectRequest):
    try:
        result = await client_manager.connect(request.db_type, request.db_url)
        return result
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "invalid choice" in error_msg:
            error_msg = f"Invalid database type. Please choose from: postgres, mysql, mongodb, or sqlite"
        elif "RFC 3986" in error_msg or "quote_plus" in error_msg:
            error_msg = "MongoDB connection string contains special characters. Please URL-encode your username and password using urllib.parse.quote_plus() or use a connection string without special characters."
        elif "Connection refused" in error_msg or "could not connect" in error_msg.lower():
            error_msg = "Could not connect to database. Please check your connection string and ensure the database is running."
        elif "authentication failed" in error_msg.lower():
            error_msg = "Authentication failed. Please check your username and password."
        
        raise HTTPException(status_code=400, detail=error_msg)


@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        result = await client_manager.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def status():
    return {"connected": client_manager.connected}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
