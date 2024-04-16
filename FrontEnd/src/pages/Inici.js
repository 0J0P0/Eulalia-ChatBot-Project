import React from 'react';

import '../styles/inici.css';

import MainLogo from '../components/MainLogo.js';
import Login from '../components/Login.js';

import backgound_img from '../img/inici_background.jpg';

function Inici() {
  return (
    <div>
      <img className='background_img' src={backgound_img}/>
      <MainLogo />
      <Login />
    </div>
  );
}

export default Inici;
