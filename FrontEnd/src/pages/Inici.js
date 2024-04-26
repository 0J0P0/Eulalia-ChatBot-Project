import React from 'react';

import '../styles/inici.css';

import MainLogo from '../components/MainLogo.js';
import Login from '../components/Login.js';

import backgound_img from '../img/inici_background.jpg';

function Inici({ authenticateUser }) {
  return (
    <div>
      <img className='background_img' src={backgound_img} alt="background"/>
      <MainLogo />
      <Login authenticateUser={authenticateUser} />
    </div>
  );
}

export default Inici;
