import React from 'react';
import { Link } from 'react-router-dom';

import '../styles/sidebar.css';

const SideBar = props => {
    const sidebarClass = props.isOpen ? "sidebar open" : "sidebar";

    const handleLogout = () => {
        // Clear authentication status and remove token from localStorage
        localStorage.removeItem('authenticated');
        // Update authentication status
        props.authenticateUser(false);
    };

    return (
      <div className={sidebarClass}>
        <div className='sidebar_links'>
            <ul>
                <li><Link to='/'>Inici</Link></li>
                <li><Link to='/bot'>Eulàlia</Link></li>
                <li><Link to='/quisom'>Qui som?</Link></li>
                <li><Link to='/ajuda'>Ajuda</Link></li>
                {props.authenticated && (
                    <li><button className='logout_button' onClick={handleLogout}>Tanca Sessió</button></li>
                )}
            </ul>
        </div>
      </div>
    );
}

export default SideBar;
