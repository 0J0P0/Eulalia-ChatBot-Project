import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import axios from 'axios';

import '../styles/login.css';

function Login() {
  const [showPopup, setShowPopup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  // Function to show/hide the login popup
  function togglePopup() {
    setShowPopup(!showPopup);
  }

  // Function to handle the username input
  function handleUsernameChange(event) {
    setUsername(event.target.value);
  }

  // Function to handle the password input
  function handlePasswordChange(event) {
    setPassword(event.target.value);
  }

  // Function to handle the user login
  function handleUser(event) {
    event.preventDefault();
    axios.post('http://127.0.0.1:5000/login', { username, password })
      .then(response => {
        console.log(response.data);
        if (response.data.success) {
          // Redirect to the bot page
          navigate('/bot');
        }
        else {
          setErrorMessage('El teu usuari o contrasenya són incorrectes');
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
    <div>
      <button id="boto" onClick={togglePopup}>Inicia sessió</button>
      {showPopup && (
        <div className="login_container">
          <p className="welcome_text">Benvingut a Eulàlia!</p>
          
          <input type="text" placeholder="Usuari" value={username} onChange={handleUsernameChange} />
          <input type="password" placeholder="Contrasenya" value={password} onChange={handlePasswordChange} />
          
          <button className='submit-button' onClick={handleUser}>Enviar</button>
          {errorMessage && <p className="error_message">{errorMessage}</p>}
          <button className='close-button' onClick={togglePopup}>Tancar</button>
        </div>
      )}
    </div>
  );
};

export default Login;
