import logo from './logo.svg';
import './styles/App.css';
import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/header.js'
import SideBar from './components/sidebar.js';
import Quisom from './pages/Quisom.js';
import Chat from './pages/Chat.js';
import Ajuda from './pages/Ajuda.js';

function App() {
  const [sidebarOpen, setSideBarOpen] = useState(false);
  
  const handleViewSidebar = () => {
    setSideBarOpen(!sidebarOpen);
  };
  
  return (
    <Router>
      {/* <Home /> */}
      <Header onClick={handleViewSidebar} />
      <SideBar isOpen={sidebarOpen}/>
      <p>
      </p>
        <Routes>
          <Route path='/quisom' element={<Quisom/>} />
          <Route path='/chat' element={<Chat/>} />
          <Route path='/ajuda' element={<Ajuda/>} />
        </Routes>
    </Router>
);
}

export default App;
