import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { CSVLink } from 'react-csv';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28BFE', '#FEA8B0'];

const ReportsPage = () => {
  const [contacts, setContacts] = useState([]);
  const [pipelineData, setPipelineData] = useState([]);
  const [leadsTrend, setLeadsTrend] = useState([]);
  const [leadSources, setLeadSources] = useState([]);

  useEffect(() => {
    fetch(`${BACKEND_API}/api/contacts`)
      .then(res => res.json())
      .then(data => setContacts(data.items || []));
    fetch(`${BACKEND_API}/api/reports/pipeline-summary`)
      .then(res => res.json())
      .then(data => setPipelineData(data.items || []));
    fetch(`${BACKEND_API}/api/reports/leads-trend`)
      .then(res => res.json())
      .then(data => setLeadsTrend(data.items || []));
    fetch(`${BACKEND_API}/api/reports/lead-sources`)
      .then(res => res.json())
      .then(data => setLeadSources(data.items || []));
  }, []);

  return (
    <div className="reports-page">
      <h1 className="page-title">Reports Dashboard</h1>
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <CSVLink data={contacts} filename="contacts.csv" className="export-btn">
          Export All Contacts
        </CSVLink>
      </div>
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <h2>Sales Pipeline by Stage</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={pipelineData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#0088FE" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <h2>New Leads Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={leadsTrend} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#00C49F" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <h2>Lead Sources</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={leadSources} dataKey="count" nameKey="source" cx="50%" cy="50%" outerRadius={100} label>
              {leadSources.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ReportsPage;