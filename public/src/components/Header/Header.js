import React from 'react';
import './Header.css';
import LiveDateTime from './LiveDateTime';
import { FiLogOut, FiMenu } from 'react-icons/fi';

// `onLogout` is passed from App.js
const Header = ({ onLogout, toggleSidebar, isSidebarCollapsed }) => {
  return (
    <header className="header">
      <div className="header-left">
        <button className="header-menu-toggle" onClick={toggleSidebar}>
          <FiMenu />
        </button>
        <span className="header-welcome">
          Welcome, **Your Name** {/* In a real app, you would get this from user context, e.g.:
            Welcome, {user.firstName}
          */}
        </span>
      </div>
      
      <div className="header-right">
        <LiveDateTime />
        
        <div className="header-user">
          <div className="user-avatar">
            YN 
            {/* Placeholder. Replace with <img src={user.avatarUrl} /> */}
          </div>
          <div className="user-info">
            <span className="user-name">Your Name</span>
            <span className="user-role">Administrator</span>
          </div>
        </div>
        
        <button className="logout-button" onClick={onLogout}>
          <FiLogOut />
          <span className="logout-text">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Header;