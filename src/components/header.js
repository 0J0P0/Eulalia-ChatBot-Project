import React from 'react'
import '../styles/header.css'
import nav_icon from '../img/nav_list.svg'
import nav_bcn_logo from '../img/nav_bcn_logo.png'

const Header = props => {
    return (
    <div className='header'>
        <div className='imgContainer'>
            <img className='nav_list_icon' src={nav_icon} alt='Navigation List' onClick={props.onClick}/>
        </div>
        <div className='imgContainer'>
            <img className='nav_bcn' src={nav_bcn_logo} alt='Barcelona Logo'/>
        </div>
    </div>
    );
}

export default Header;