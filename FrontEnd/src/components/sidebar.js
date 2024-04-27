import { React } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import '../styles/sidebar.css';

import logoutImg from '../img/logout.svg';

const SideBar = props => {
  const navigate = useNavigate();
  const sidebarClass = props.isOpen ? "sidebar open" : "sidebar";

  const handleLogout = () => {
      props.authenticateUser(false);
      navigate('/');
  };  

  return (
    <div className={sidebarClass}>
      <div className='sidebar_links'>
        <ul>
          <li><Link to='/'>Inici</Link></li>
          {props.authenticated && (
            <li><Link to='/bot'>Eulàlia</Link></li>
          )}
          {!props.authenticated && (
            <li><Link to='/'>Eulàlia</Link></li>
          )}
          <li><Link to='/quisom'>Qui som?</Link></li>
          <li><Link to='/ajuda'>Ajuda</Link></li>
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
    </div>
  );
}

export default SideBar;
