# MCP Database Client with UI

Complete setup guide for running the MCP database client with a React frontend.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  React Frontend │ ───> │  FastAPI Server │ ───> │   MCP Server    │
│  (Port 3000)    │      │  (Port 8000)    │      │  (Database)     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Backend API Server

```bash
python api_server.py
```

The API server will start on `http://localhost:8000`

### 4. Start the Frontend (in a new terminal)

```bash
cd frontend
npm install
npm start
```

The React app will open at `http://localhost:3000`

## Usage

1. **Connect to Database**
   - Click the "Connect" button in the header
   - Or modify the connection settings in the frontend code

2. **Query Your Database**
   - Type natural language queries like:
     - "Show me all tables"
     - "Get the first 10 rows from users table"
     - "Update passport where id = xyz"
     - "What are the columns in the passports table?"

3. **View Results**
   - Switch between Table, JSON, and Auto views
   - Scroll through large datasets
   - Copy data as needed

## Features

### Frontend
- ✨ Modern, gradient-based UI design
- 📊 Multiple view modes (Table, JSON, Text)
- 🔄 Real-time connection status
- 📱 Fully responsive
- 🎨 Smooth animations and transitions

### Backend
- 🚀 FastAPI for high performance
- 🤖 OpenAI integration for natural language queries
- 🔌 MCP protocol support
- 🔒 CORS enabled for local development
- 📡 RESTful API endpoints

### Database Support
- PostgreSQL
- MySQL
- MongoDB
- SQLite

## API Endpoints

### POST /api/connect
Connect to a database.

**Request:**
```json
{
  "db_type": "postgres",
  "db_url": "postgresql://user:pass@host:port/db"
}
```

**Response:**
```json
{
  "status": "connected",
  "tools": ["health_check", "get_tables", "execute_query", ...]
}
```

### POST /api/query
Execute a natural language query.

**Request:**
```json
{
  "query": "Show me the first 5 rows from users table"
}
```

**Response:**
```json
{
  "response": "Here are the first 5 rows...",
  "data": [...]
}
```

### GET /api/status
Check connection status.

**Response:**
```json
{
  "connected": true
}
```

## Configuration

### Frontend Configuration
Edit `frontend/src/App.js` to change default connection settings:

```javascript
const result = await axios.post('/api/connect', {
  db_type: 'postgres',
  db_url: process.env.REACT_APP_DB_URL || 'your_default_url'
});
```

### Backend Configuration
Edit `api_server.py` to change:
- Port: Change `uvicorn.run(app, host="0.0.0.0", port=8000)`
- CORS origins: Modify `allow_origins` in CORS middleware
- OpenAI model: Change `MODEL_NAME` variable

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `api_server.py`
- Verify proxy setting in `frontend/package.json`

### Database connection fails
- Verify database URL format
- Check database credentials
- Ensure database server is accessible

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits
- Ensure model name is correct

## Development

### Frontend Development
```bash
cd frontend
npm start
```

### Backend Development
```bash
python api_server.py
```

Or with auto-reload:
```bash
uvicorn api_server:app --reload --port 8000
```

## Production Deployment

### Frontend
```bash
cd frontend
npm run build
```

Serve the `build` folder with any static file server.

### Backend
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Security Notes

- Never commit `.env` files with real credentials
- Use environment variables for sensitive data
- Implement authentication for production use
- Restrict CORS origins in production
- Use HTTPS in production

## License

MIT
