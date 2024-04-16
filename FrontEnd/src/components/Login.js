import React, { useState } from 'react';
import { Link } from 'react-router-dom';
<<<<<<< HEAD
=======

>>>>>>> e0c4b7cfb78108b6e358c64bf3ad5b9cd17f14e0
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

<<<<<<< HEAD
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
=======
  // function SendUser() {
  //   fetch('http://localhost:3000', {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify({ username, password }),
  //   })
  //     .then(response => {
  //       return response.text();
  //     })
  //     .then(data => {
  //       alert(data);
  //       setUsername('');
  //       setPassword('');
  //       togglePopup();
  //     })
  //     .catch(error => {
  //       console.error('Error sending user:', error);
  //     });
  // }

   // Function to send user data to server
   const SendUser = async () => {
    // Implement logic to send user data to server
    try {
      const response = await fetch('http://localhost:3000/api/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      console.log(data); // Optionally handle response from server
    } catch (error) {
      console.error('Error sending user data:', error);
    }
  };
>>>>>>> e0c4b7cfb78108b6e358c64bf3ad5b9cd17f14e0

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
