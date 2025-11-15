import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';
import logo from '../../assets/RoshTech_Industries_NO BACKGROUND.png';
import {
  FiGrid, FiUsers, FiUser, FiTarget, FiTrendingUp, FiCheckSquare,
  FiCalendar, FiBarChart2, FiSettings, FiChevronsLeft, FiChevronsRight
} from 'react-icons/fi'; // Using Feather Icons

const Sidebar = ({ isCollapsed, toggleSidebar }) => {
  const navItems = [
    { name: 'Dashboard', icon: <FiGrid />, path: '/' },
    { name: 'Leads', icon: <FiTarget />, path: '/leads' },
    { name: 'Accounts', icon: <FiUsers />, path: '/accounts' },
    { name: 'Contacts', icon: <FiUser />, path: '/contacts' },
    { name: 'Opportunities', icon: <FiTrendingUp />, path: '/opportunities' },
    { name: 'Tasks', icon: <FiCheckSquare />, path: '/tasks' },
    { name: 'Calendar', icon: <FiCalendar />, path: '/calendar' },
    { name: 'Reports', icon: <FiBarChart2 />, path: '/reports' },
    { name: 'User Management', icon: <FiUsers />, path: '/users' },
    { name: 'Settings', icon: <FiSettings />, path: '/settings' },
  ];

  return (
    <nav className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <img 
          src={logo} 
          alt="Roshtech Logo" 
          className="sidebar-logo"
        />
        <span className="sidebar-logo-text">Roshtech CRM</span>
      </div>

      <button className="sidebar-toggle" onClick={toggleSidebar}>
        {isCollapsed ? <FiChevronsRight /> : <FiChevronsLeft />}
      </button>

      <ul className="sidebar-menu">
        {navItems.map((item) => (
          <li key={item.name} className="sidebar-menu-item">
            <NavLink 
              to={item.path}
              className={({ isActive }) => 
                `sidebar-menu-link ${isActive ? 'active' : ''}`
              }
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-text">{item.name}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Sidebar;