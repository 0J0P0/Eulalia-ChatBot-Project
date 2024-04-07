import React from 'react';

import { Link } from 'react-router-dom';

import '../styles/login.css';

const Login = () => {
  return (
    <div className='login'>
      <ul>
        <li>
          <Link to="/Chat" id="boto">Inicia sessió</Link>
        </li>
      </ul>
    </div>
  );
};

export default Login;
