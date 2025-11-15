import React, { useState, useEffect } from 'react';

const BACKEND_API = 'http://localhost:5000';
const statusOptions = [
  'Prospecting',
  'Qualification',
  'Needs Analysis',
  'Proposal',
  'Negotiation',
  'Closed Won',
  'Closed Lost'
];

const OpportunityModal = ({ isOpen, onClose, opportunityToEdit, onSave }) => {
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({
    name: '',
    account_id: '',
    value: '',
    status: 'Prospecting',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${BACKEND_API}/api/accounts`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setAccounts(data.items);
      });
  }, []);

  useEffect(() => {
    if (opportunityToEdit) {
      setForm({
        name: opportunityToEdit.name || '',
        account_id: opportunityToEdit.account_id || '',
        value: opportunityToEdit.value || '',
        status: opportunityToEdit.status || 'Prospecting',
      });
    } else {
      setForm({ name: '', account_id: '', value: '', status: 'Prospecting' });
    }
  }, [opportunityToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (opportunityToEdit) {
        res = await fetch(`${BACKEND_API}/api/opportunities/${opportunityToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      } else {
        res = await fetch(`${BACKEND_API}/api/opportunities`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save opportunity');
      }
    } catch (err) {
      alert('Error saving opportunity');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{opportunityToEdit ? 'Edit Opportunity' : 'Add Opportunity'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Opportunity Name</label>
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Account</label>
            <select value={form.account_id} onChange={e => setForm({ ...form, account_id: e.target.value })} required>
              <option value="">Select Account</option>
              {accounts.map(acc => (
                <option key={acc.id} value={acc.id}>{acc.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Value</label>
            <input type="number" value={form.value} onChange={e => setForm({ ...form, value: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Status</label>
            <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} required>
              {statusOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>{opportunityToEdit ? 'Update' : 'Add'} Opportunity</button>
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OpportunityModal;
