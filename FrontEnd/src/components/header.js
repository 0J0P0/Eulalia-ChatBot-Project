import React from 'react'

import '../styles/header.css'

import nav_icon from '../img/nav_list.svg'
import nav_bcn_logo from '../img/nav_bcn_logo.png'

const Header = props => {
  return (
    <div className='header'>
      <img className='nav_list_icon' src={nav_icon} alt='Navigation List' onClick={props.onClick}/>
      <img className='nav_bcn' src={nav_bcn_logo} alt='Barcelona Logo'/>
    </div>
  );
}

export default Header;