import React, { useState } from "react";
import { Database, Loader2, XCircle } from "lucide-react";
import "./ConnectionPage.css";

function ConnectionPage({ onConnect, loading, error }) {
  const [dbType, setDbType] = useState("postgres");
  const [dbUrl, setDbUrl] = useState("");
  const [localError, setLocalError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError("");

    if (!dbUrl.trim()) {
      setLocalError("Please enter a database URL");
      return;
    }

    try {
      await onConnect(dbType, dbUrl);
    } catch (err) {
      // Error is handled by parent component
    }
  };

  const dbExamples = {
    postgres: "postgresql://user:password@host:5432/database",
    mysql: "mysql://user:password@host:3306/database",
    mongo: "mongodb+srv://user:password@cluster.mongodb.net/database",
    sqlite: "sqlite:///path/to/database.db",
  };

  return (
    <div className="connection-page">
      <div className="connection-container">
        <div className="connection-header">
          <Database className="connection-icon" size={48} />
          <h1>Connect to Database</h1>
          <p>Enter your database credentials to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="connection-form">
          <div className="form-group">
            <label htmlFor="db-type">Database Type</label>
            <select
              id="db-type"
              value={dbType}
              onChange={(e) => setDbType(e.target.value)}
              className="form-select"
              disabled={loading}
            >
              <option value="postgres">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="mongo">MongoDB</option>
              <option value="sqlite">SQLite</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="db-url">Database URL</label>
            <input
              id="db-url"
              type="text"
              value={dbUrl}
              onChange={(e) => setDbUrl(e.target.value)}
              placeholder={dbExamples[dbType]}
              className="form-input"
              disabled={loading}
            />
            <small className="form-hint">
              Example: {dbExamples[dbType]}
              {dbType === "mongo" && (
                <>
                  <br />
                  Note: Add /database_name at the end. Special characters in
                  credentials are auto-encoded.
                </>
              )}
            </small>
          </div>

          {(error || localError) && (
            <div className="error-message">
              <XCircle size={20} />
              <span>{error || localError}</span>
            </div>
          )}

          <button
            type="submit"
            className="connect-button"
            disabled={loading || !dbUrl.trim()}
          >
            {loading ? (
              <>
                <Loader2 className="spinner" size={20} />
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <Database size={20} />
                <span>Connect to Database</span>
              </>
            )}
          </button>
        </form>

        <div className="connection-footer">
          <p>🔒 Your credentials are secure and never stored</p>
        </div>
      </div>
    </div>
  );
}

export default ConnectionPage;
