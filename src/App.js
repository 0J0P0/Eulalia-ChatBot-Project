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
        <div className='flex'>
          <SideBar isOpen={sidebarOpen}/>
          <div className='sidebar_content'>
            <Routes>
              <Route path='/quisom' element={<Quisom/>} />
            </Routes>
          </div>
        </div>
    </Router>
  );
}

export default App;
