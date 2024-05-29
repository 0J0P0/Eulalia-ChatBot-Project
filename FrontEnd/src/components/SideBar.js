import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PopUp from './PopUp';

import '../styles/sidebar.css';
import logoutImg from '../img/logout.svg';

const SideBar = (props) => {
  const [showPopUp, setShowPopUp] = useState(false);
  const navigate = useNavigate();
  const sidebarClass = props.isOpen ? "sidebar open" : "sidebar";

  useEffect(() => {
    if (!props.authenticated && showPopUp) {
      navigate('/');
    }
  }, [props.authenticated, showPopUp, navigate]);

  const handleLogout = () => {
    props.authenticateUser(false);
    navigate('/');
  };

  const handleEulaliaClick = () => {
    if (!props.authenticated) {
      setShowPopUp(true);
    }
  };

  const closePopUp = () => {
    setShowPopUp(false);
  };

  const handleLinkClick = () => {
    props.closeSidebar();
  };

  return (
    <div className={sidebarClass}>
      <div className='sidebar_links'>
        <ul>
          <li><Link to='/' onClick={handleLinkClick} >Inici</Link></li>
          {props.authenticated ? (
            <li><Link to='/bot ' onClick={handleLinkClick}>Eulàlia</Link></li>
          ) : (
            <li><a href='#' onClick={handleEulaliaClick}>Eulàlia</a></li>
          )}
          <li><Link to='/quisom ' onClick={handleLinkClick}>Qui som?</Link></li>
          <li><Link to='/ajuda ' onClick={handleLinkClick}>Ajuda</Link></li>
          {props.authenticated && (
            <li className="logout_container">
              <button className='logout_button' onClick={handleLogout}>
                <img src={logoutImg} alt="logout" className="logout_icon" />
                Tanca Sessió
              </button>
            </li>
          )}
        </ul>
      </div>
      {showPopUp && (
        <PopUp
          message="Recorda iniciar sessió"
          onClose={closePopUp}
        />
      )}
    </div>
  );
}

export default SideBar;
