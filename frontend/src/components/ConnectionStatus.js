import React from 'react';
import { CheckCircle, XCircle, Circle, Plug } from 'lucide-react';
import './ConnectionStatus.css';

function ConnectionStatus({ status, onConnect }) {
  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return <CheckCircle size={20} />;
      case 'error':
        return <XCircle size={20} />;
      default:
        return <Circle size={20} />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'error':
        return 'Error';
      default:
        return 'Disconnected';
    }
  };

  return (
    <div className="connection-status">
      <div className={`status-indicator ${status}`}>
        {getStatusIcon()}
        <span>{getStatusText()}</span>
      </div>
      {status !== 'connected' && (
        <button className="connect-button" onClick={onConnect}>
          <Plug size={18} />
          Connect
        </button>
      )}
    </div>
  );
}

export default ConnectionStatus;
