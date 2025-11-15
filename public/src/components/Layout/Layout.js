import React, { useState } from 'react';
import Sidebar from '../SideBar/Sidebar';
import Header from '../Header/Header';
import './Layout.css';

const Layout = ({ children, onLogout }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className={`layout-container ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar 
        isCollapsed={isSidebarCollapsed} 
        toggleSidebar={toggleSidebar} 
      />
      
      <div className="main-content">
        <Header 
          onLogout={onLogout} 
          toggleSidebar={toggleSidebar} 
          isSidebarCollapsed={isSidebarCollapsed} 
        />
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;