import React from 'react';

import '../styles/main_logo.css';

import main_eulalia_logo from '../img/main_eulalia_logo.png';


function Logo() {
  return (
    <div className='main_logo_container'>
      <div>
        <img className='logo_img' src={main_eulalia_logo} alt='Eulalia Logo'/>
      </div>
      <div>
        <h1>
          <span class="black-text">Eulàl</span>
          <span class="blue-text">ia</span>
        </h1>
      </div>
      <div className='page_subtitle'>
        <h2> FEM BARCELONA </h2>
      </div>
    </div>
  );
};

export default Logo;