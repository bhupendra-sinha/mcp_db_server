import React from 'react';
import { CheckCircle } from 'lucide-react';
import './SuccessMessage.css';

function SuccessMessage({ message }) {
  return (
    <div className="success-message">
      <CheckCircle size={20} />
      <span>{message}</span>
    </div>
  );
}

export default SuccessMessage;
