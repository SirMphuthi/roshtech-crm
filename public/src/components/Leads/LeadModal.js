import React, { useState, useEffect } from 'react';

const BACKEND_API = 'http://localhost:5000';

const statusOptions = ['New', 'Contacted', 'Qualified', 'Converted', 'Lost'];

const LeadModal = ({ isOpen, onClose, leadToEdit, onSave }) => {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    company: '',
    email: '',
    phone: '',
    status: 'New',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (leadToEdit) {
      setForm({
        first_name: leadToEdit.first_name || '',
        last_name: leadToEdit.last_name || '',
        company: leadToEdit.company || '',
        email: leadToEdit.email || '',
        phone: leadToEdit.phone || '',
        status: leadToEdit.status || 'New',
      });
    } else {
      setForm({ first_name: '', last_name: '', company: '', email: '', phone: '', status: 'New' });
    }
  }, [leadToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (leadToEdit) {
        res = await fetch(`${BACKEND_API}/api/leads/${leadToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      } else {
        res = await fetch(`${BACKEND_API}/api/leads`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save lead');
      }
    } catch (err) {
      alert('Error saving lead');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{leadToEdit ? 'Edit Lead' : 'Add Lead'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>First Name</label>
            <input type="text" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Last Name</label>
            <input type="text" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Company</label>
            <input type="text" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input type="text" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
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
            <button type="submit" disabled={loading}>{leadToEdit ? 'Update' : 'Add'} Lead</button>
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LeadModal;
