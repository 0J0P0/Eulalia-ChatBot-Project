import React from 'react';

import { Link } from 'react-router-dom';

import '../styles/login.css';

const Login = () => {
  return (
    <li>
      <Link className='login' to="/bot" id="boto">Inicia sessió</Link>
    </li>
  );
};

export default Login;
