import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/login.css';

const Login = () => {
  const [showPopup, setShowPopup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  function togglePopup() {
    setShowPopup(!showPopup);
  }

  function handleUsernameChange(event) {
    setUsername(event.target.value);
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value);
  }

  function SendUser() {
    fetch('http://localhost:3000', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    })
      .then(response => {
        return response.text();
      })
      .then(data => {
        alert(data);
        setUsername('');
        setPassword('');
        togglePopup();
      })
      .catch(error => {
        console.error('Error sending user:', error);
      });
  }

  return (
    <li>
      <Link className='login' to="/bot" id="boto">Inicia sessió</Link>
      <button className='login' id="boto_2" onClick={togglePopup}>Crea el teu usuari</button>
      {showPopup && (
        <div className="popup-container">
          <p className="welcome-text">Benvingut a Eulàlia!</p>
          <input type="text" placeholder="Username" value={username} onChange={handleUsernameChange} />
          <input type="password" placeholder="Password" value={password} onChange={handlePasswordChange} />
          <button className='submit-button' onClick={SendUser}>Submit</button>
          <button className='close-button' onClick={togglePopup}>Close</button>
        </div>
      )}
    </li>
  );
};

export default Login;
