import React from 'react';
import '../styles/popup.css';

const PopUp = ({ message, onClose }) => {
  return (
    <div className="popup-overlay">
      <div className="popup">
        <span className="popup-message">{message}</span>
        <button className="popup-close-button" onClick={onClose}>Tancar</button>
      </div>
    </div>
  );
};

export default PopUp;
