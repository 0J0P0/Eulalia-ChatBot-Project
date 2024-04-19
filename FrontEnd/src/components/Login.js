import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import axios from 'axios';


import '../styles/login.css';

function Login() {
  const [showPopup, setShowPopup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  function togglePopup() {
    setShowPopup(!showPopup);
  }

  function handleUsernameChange(event) {
    setUsername(event.target.value);
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value);
  }

  function handleUser(event) {
    event.preventDefault();
    axios.post('http://localhost:8081/login', { username, password })
      .then(response => {
        console.log(response.data);
        if (response.data.length > 0){
          // Redirect to the bot page
          navigate('/bot');
        }
      })
      .catch(error => {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.log(error.response.data);
          console.log(error.response.status);
          console.log(error.response.headers);
        } else if (error.request) {
          // The request was made but no response was received
          console.log(error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error', error.message);
        }
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
          <button className='submit-button' onClick={handleUser}>Submit</button>
          <button className='close-button' onClick={togglePopup}>Close</button>
        </div>
      )}
    </li>
  );
};

export default Login;
