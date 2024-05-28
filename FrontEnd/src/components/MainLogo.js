import React from 'react';

import '../styles/main_logo.css';

import main_eulalia_logo from '../img/main_eulalia_logo.png';

function MainLogo() {
  return (
    <div className='main_logo_container'>
      <img className='logo_img' src={main_eulalia_logo} alt='Eulalia MainLogo'/>
      <h1>
        <span class="black-text">Eulàl</span>
        <span class="blue-text">ia</span>
      </h1>
      <div className='page_subtitle'>
        <h2> OBRIM BARCELONA </h2>
      </div>
    </div>
  );
};

export default MainLogo;