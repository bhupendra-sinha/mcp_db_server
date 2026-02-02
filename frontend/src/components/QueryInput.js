import React from 'react';
import { Send } from 'lucide-react';
import './QueryInput.css';

function QueryInput({ query, setQuery, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} className="query-input-form">
      <div className="input-wrapper">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about your database... (e.g., 'Show me the first 5 rows from users table' or 'Update passport where id = ...')"
          className="query-textarea"
          rows={3}
          disabled={loading}
        />
        <button
          type="submit"
          className="submit-button"
          disabled={loading || !query.trim()}
        >
          <Send size={20} />
          <span>Send Query</span>
        </button>
      </div>
    </form>
  );
}

export default QueryInput;
