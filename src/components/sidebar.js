import React, { useState } from 'react';

import '../styles/sidebar.css';

const SideBar = props => {
    const sidebarClass = props.isOpen ? "sidebar open" : "sidebar";
    return (
      <div className={sidebarClass}>
        <div className='sidebar_links'>
            <ul>
                <li><a href='./App.js'>Inici</a></li>
                <li><a href='./Quisom.js'>Qui som?</a></li>
                <li><a href='#'>Ajuda</a></li>
            </ul>
        </div>
      </div>
    );
}

export default SideBar;
