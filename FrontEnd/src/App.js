import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/Header.js';
import SideBar from './components/SideBar.js';

import './styles/App.css';

import Inici from './pages/Inici.js';
import Quisom from './pages/Quisom.js';
import Bot from './pages/Bot.js';
import Ajuda from './pages/Ajuda.js';

export const metadata = {
  title: 'Eulàlia Chat'
}

function App() {
  const [sidebarOpen, setSideBarOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const isAuthenticated = localStorage.getItem('authenticated');
    if (isAuthenticated === 'true') {
      setAuthenticated(true);
    }
  }, []);

  const handleViewSidebar = () => {
    setSideBarOpen(!sidebarOpen);
  };

  const authenticateUser = (status) => {
    setAuthenticated(status);
    // Update authentication status in localStorage
    localStorage.setItem('authenticated', status);
  };

  return (
    <div className='main_container'>
      <Router>
        <Header onClick={handleViewSidebar} />
        <SideBar isOpen={sidebarOpen} authenticated={authenticated} authenticateUser={authenticateUser} />
        <Routes>
          <Route path='/' element={<Inici authenticateUser={authenticateUser} />} />
          <Route path='/bot' element={<Bot />} />
          <Route path='/quisom' element={<Quisom />} />
          <Route path='/ajuda' element={<Ajuda />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
