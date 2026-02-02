import React, { useState } from "react";
import { Table, List, Code } from "lucide-react";
import "./ResponseDisplay.css";
import DataTable from "./DataTable";

function ResponseDisplay({ response }) {
  const [viewMode, setViewMode] = useState("auto");

  const detectResponseType = () => {
    if (!response) return "text";

    if (typeof response === "string") return "text";

    // Check if response has data array
    if (
      response.data &&
      Array.isArray(response.data) &&
      response.data.length > 0
    ) {
      return "table";
    }

    if (
      response.result &&
      Array.isArray(response.result) &&
      response.result.length > 0
    ) {
      return "table";
    }

    if (Array.isArray(response) && response.length > 0) {
      return "table";
    }

    // If it's an object with just a response field, it's text
    if (response.response && typeof response.response === "string") {
      return "text";
    }

    return "text";
  };

  const responseType = viewMode === "auto" ? detectResponseType() : viewMode;

  const getDisplayData = () => {
    // Extract the actual data to display
    if (response.data && Array.isArray(response.data)) {
      return response.data;
    }
    if (response.result && Array.isArray(response.result)) {
      return response.result;
    }
    if (Array.isArray(response)) {
      return response;
    }
    return null;
  };

  const getTextContent = () => {
    if (typeof response === "string") return response;
    if (response.response) return response.response;
    return JSON.stringify(response, null, 2);
  };

  const renderContent = () => {
    if (responseType === "table") {
      const data = getDisplayData();
      if (data && data.length > 0) {
        return <DataTable data={data} />;
      }
      // Fallback to text if no table data
      return <div className="text-view">{getTextContent()}</div>;
    }

    if (responseType === "json") {
      return (
        <pre className="json-view">{JSON.stringify(response, null, 2)}</pre>
      );
    }

    // Text view
    return <div className="text-view">{getTextContent()}</div>;
  };

  return (
    <div className="response-display">
      <div className="response-header">
        <h2>Response</h2>
        <div className="view-controls">
          <button
            className={`view-button ${viewMode === "auto" ? "active" : ""}`}
            onClick={() => setViewMode("auto")}
          >
            <List size={18} />
            Auto
          </button>
          <button
            className={`view-button ${viewMode === "table" ? "active" : ""}`}
            onClick={() => setViewMode("table")}
          >
            <Table size={18} />
            Table
          </button>
          <button
            className={`view-button ${viewMode === "json" ? "active" : ""}`}
            onClick={() => setViewMode("json")}
          >
            <Code size={18} />
            JSON
          </button>
        </div>
      </div>
      <div className="response-content">{renderContent()}</div>
    </div>
  );
}

export default ResponseDisplay;
