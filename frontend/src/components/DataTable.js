import React from 'react';
import './DataTable.css';

function DataTable({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <div className="no-data">No data to display</div>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>
                  {typeof row[col] === 'object' 
                    ? JSON.stringify(row[col]) 
                    : String(row[col] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        Showing {data.length} row{data.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}

export default DataTable;
