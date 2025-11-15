import React, { useState, useEffect } from 'react';
import LeadModal from '../components/Leads/LeadModal';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000';

const LeadsPage = () => {
  const [leads, setLeads] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [leadToEdit, setLeadToEdit] = useState(null);

  const fetchLeads = () => {
    fetch(`${BACKEND_API}/api/leads`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setLeads(data.items);
        else setLeads([]);
      })
      .catch(err => console.error('Failed to fetch leads:', err));
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const handleDelete = async (leadId) => {
    const res = await fetch(`${BACKEND_API}/api/leads/${leadId}`, { method: 'DELETE' });
    if (res.ok) {
      fetchLeads();
    } else {
      alert('Failed to delete lead');
    }
  };

  return (
    <div className="leads-page">
      <h1 className="page-title">Leads</h1>
      <button
        className="add-lead-btn"
        onClick={() => {
          setIsModalOpen(true);
          setLeadToEdit(null);
        }}
        style={{ marginBottom: '1rem' }}
      >
        Add Lead
      </button>
      <table className="leads-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {leads.length === 0 ? (
            <tr><td colSpan={5}>No leads found.</td></tr>
          ) : (
            leads.map(lead => (
              <tr key={lead.id}>
                <td>{lead.first_name} {lead.last_name}</td>
                <td>{lead.company}</td>
                <td>{lead.email}</td>
                <td>{lead.status}</td>
                <td>
                  <button onClick={() => { setLeadToEdit(lead); setIsModalOpen(true); }}>Edit</button>
                  <button onClick={() => handleDelete(lead.id)}>Delete</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      <LeadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        leadToEdit={leadToEdit}
        onSave={fetchLeads}
      />
    </div>
  );
};

export default LeadsPage;