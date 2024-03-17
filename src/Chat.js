import React, { useState } from 'react'
import Header from './components/header.js'
import SideBar from './components/sidebar.js';

function Chat() {
    const [sidebarOpen, setSideBarOpen] = useState(false);
    
    const handleViewSidebar = () => {
      setSideBarOpen(!sidebarOpen);
    };
    
    return (
    <div>
        <Header onClick={handleViewSidebar} />
        <SideBar isOpen={sidebarOpen}/>
    </div>
  );
}

export default Chat;
