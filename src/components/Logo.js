import React from 'react';

import '../styles/logo.css';

import main_eulalia_logo from '../img/main_eulalia_logo.png';

function Logo({ subtitle }) {
  return (
    <div className='logo_container'>
      <img className='logo_img' src={main_eulalia_logo} alt='Eulalia Logo'/>
      <h1>
        <span class="black-text">Eulàl</span>
        <span class="blue-text">ia</span>
      </h1>
      <div className='page_subtitle'>
        <h2> {subtitle} </h2>
      </div>
    </div>
  );
};

export default Logo;