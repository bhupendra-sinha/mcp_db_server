import React, { useState } from "react";
import axios from "axios";
import { Database, Loader2, XCircle } from "lucide-react";
import "./App.css";
import QueryInput from "./components/QueryInput";
import ResponseDisplay from "./components/ResponseDisplay";
import ConnectionPage from "./components/ConnectionPage";
import SuccessMessage from "./components/SuccessMessage";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [dbInfo, setDbInfo] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await axios.post("/api/query", { query });
      setResponse(result.data);

      // Check if response contains error or success message
      if (result.data.response) {
        const responseText = result.data.response.toLowerCase();
        if (responseText.includes("error") || responseText.includes("failed")) {
          setError(result.data.response);
        } else if (
          responseText.includes("successfully") ||
          responseText.includes("inserted") ||
          responseText.includes("updated") ||
          responseText.includes("deleted")
        ) {
          setSuccess(result.data.response);
        }
      }
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || err.response?.data?.error || err.message;
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (dbType, dbUrl) => {
    setLoading(true);
    setError(null);

    try {
      const result = await axios.post("/api/connect", {
        db_type: dbType,
        db_url: dbUrl,
      });
      setIsConnected(true);
      setDbInfo({ type: dbType, url: dbUrl });
      setResponse({ message: "Connected successfully!", ...result.data });
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setDbInfo(null);
    setResponse(null);
    setError(null);
    setQuery("");
  };

  if (!isConnected) {
    return (
      <ConnectionPage
        onConnect={handleConnect}
        loading={loading}
        error={error}
      />
    );
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <Database className="header-icon" size={32} />
            <div>
              <h1>MCP Database Client</h1>
              <p className="db-info">Connected to {dbInfo?.type} database</p>
            </div>
          </div>
          <button className="disconnect-button" onClick={handleDisconnect}>
            Disconnect
          </button>
        </header>

        <div className="main-content">
          <QueryInput
            query={query}
            setQuery={setQuery}
            onSubmit={handleSubmit}
            loading={loading}
          />

          {success && <SuccessMessage message={success} />}

          {error && (
            <div className="error-message">
              <XCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="loading">
              <Loader2 className="spinner" size={32} />
              <p>Processing your query...</p>
            </div>
          )}

          {response && !loading && <ResponseDisplay response={response} />}
        </div>
      </div>
    </div>
  );
}

export default App;
