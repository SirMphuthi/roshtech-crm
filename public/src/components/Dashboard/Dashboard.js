import React from 'react';
import './Dashboard.css';
import StatCard from './StatCard';
import { 
  FiTarget, FiTrendingUp, FiCheckSquare, FiDollarSign, 
  FiUsers, FiActivity, FiUserPlus, FiBarChart2 
} from 'react-icons/fi';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <h1 className="page-title">Dashboard</h1>

      {/* Row 1: Stat Cards */}
      <div className="stat-cards-grid">
        <StatCard 
          title="New Leads"
          value="128"
          icon={<FiTarget />}
          trend="+15%"
          trendColor="success"
          linkTo="/leads"
        />
        <StatCard 
          title="Open Opportunities"
          value="42"
          icon={<FiTrendingUp />}
          trend="+5"
          trendColor="success"
          linkTo="/opportunities"
        />
        <StatCard 
          title="Tasks Due Today"
          value="8"
          icon={<FiCheckSquare />}
          trend="2 overdue"
          trendColor="danger"
          linkTo="/tasks"
        />
        <StatCard 
          title="Revenue (This Month)"
          value="R 85,400"
          icon={<FiDollarSign />}
          trend="-2.5%"
          trendColor="warning"
          linkTo="/reports"
        />
      </div>

      {/* Row 2: Charts and Feeds */}
      <div className="dashboard-main-grid">
        
        {/* Sales Pipeline Chart Card */}
        <div className="dashboard-card sales-pipeline">
          <h3 className="card-title">Sales Pipeline</h3>
          <div className="card-content chart-placeholder">
            {/* In a real app, you would use a library like Chart.js or Recharts here.
              e.g., <BarChart data={pipelineData} /> 
            */}
            <FiBarChart2 />
            <span>Sales Pipeline Chart Goes Here</span>
          </div>
        </div>

        {/* Recent Activity Feed Card */}
        <div className="dashboard-card recent-activity">
          <h3 className="card-title">Recent Activity</h3>
          <div className="card-content">
            <ul className="activity-feed">
              <li className="activity-item">
                <span className="activity-icon new-contact"><FiUserPlus /></span>
                <p><strong>You</strong> added new contact <strong>John Doe</strong> to <strong>TechCorp</strong>.</p>
                <span className="activity-time">2m ago</span>
              </li>
              <li className="activity-item">
                <span className="activity-icon new-lead"><FiTarget /></span>
                <p>New lead <strong>Jane Smith</strong> from <strong>WebForm</strong> assigned to you.</p>
                <span className="activity-time">30m ago</span>
              </li>
              <li className="activity-item">
                <span className="activity-icon new-opp"><FiTrendingUp /></span>
                <p><strong>Sizwe</strong> converted lead <strong>InfoSystems</strong> to an opportunity.</p>
                <span className="activity-time">1h ago</span>
              </li>
              <li className="activity-item">
                <span className="activity-icon task-complete"><FiCheckSquare /></span>
                <p>You completed task: "Follow up with TechCorp".</p>
                <span className="activity-time">3h ago</span>
              </li>
              <li className="activity-item">
                <span className="activity-icon note"><FiActivity /></span>
                <p><strong>Lerato</strong> added a note to <strong>Opportunity XYZ</strong>.</p>
                <span className="activity-time">Yesterday</span>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;