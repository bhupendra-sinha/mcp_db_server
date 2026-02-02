# MCP Database Client - Frontend

A modern React-based UI for interacting with your MCP database server.

## Features

- 🎨 Beautiful, modern UI with gradient design
- 💬 Natural language query interface
- 📊 Automatic data visualization (table, JSON, text views)
- 🔄 Real-time connection status
- 📱 Responsive design for mobile and desktop

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional):
```bash
cp .env.example .env
```

3. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Usage

1. Make sure the backend API server is running on port 8000
2. Click "Connect" to establish database connection
3. Type your query in natural language (e.g., "Show me all tables", "Get first 5 rows from users")
4. View results in table, JSON, or text format

## Backend API

The frontend expects a backend API running at `http://localhost:8000` with the following endpoints:

- `POST /api/connect` - Connect to database
- `POST /api/query` - Execute query
- `GET /api/status` - Check connection status

## Technologies

- React 18
- Axios for API calls
- Lucide React for icons
- CSS3 with modern gradients and animations
