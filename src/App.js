import logo from './logo.svg';
import './styles/App.css';
import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/header.js'
import SideBar from './components/sidebar.js';
import Quisom from './pages/Quisom.js';

function App() {
  const [sidebarOpen, setSideBarOpen] = useState(false);
  
  const handleViewSidebar = () => {
    setSideBarOpen(!sidebarOpen);
  };
  
  return (
    <Router>
      <Header onClick={handleViewSidebar} />
      <SideBar isOpen={sidebarOpen}/>
        <Routes>
          <Route path='/quisom' element={<Quisom/>} />
        </Routes>
    </Router>
);
}

export default App;
