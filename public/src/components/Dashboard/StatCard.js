import React from 'react';
import './StatCard.css';
import { Link } from 'react-router-dom';

const StatCard = ({ title, value, icon, trend, trendColor, linkTo }) => {
  return (
    <Link to={linkTo} className="stat-card-link">
      <div className="stat-card">
        <div className={`stat-icon-wrapper icon-bg-${trendColor}`}>
          {icon}
        </div>
        <div className="stat-info">
          <span className="stat-title">{title}</span>
          <span className="stat-value">{value}</span>
          <span className={`stat-trend trend-${trendColor}`}>
            {trend}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default StatCard;