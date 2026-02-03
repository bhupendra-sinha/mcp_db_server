from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp_client import client_manager
from pydantic import BaseModel
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")
    await client_manager.disconnect()

app = FastAPI(title="MCP Database API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class ConnectRequest(BaseModel):
    db_type: str
    db_url: str


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