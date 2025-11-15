import React, { useState, useEffect } from 'react';


const BACKEND_API = 'http://localhost:5000'; // Change to your backend endpoint if needed


const ContactModal = ({ isOpen, onClose, contactToEdit, onSave }) => {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    company_name: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (contactToEdit) {
      setForm({
        first_name: contactToEdit.first_name || '',
        last_name: contactToEdit.last_name || '',
        email: contactToEdit.email || '',
        phone_number: contactToEdit.phone_number || '',
        company_name: contactToEdit.company_name || '',
      });
    } else {
      setForm({ first_name: '', last_name: '', email: '', phone_number: '', company_name: '' });
    }
  }, [contactToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (contactToEdit) {
        // Update
        res = await fetch(`${BACKEND_API}/api/contacts/${contactToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      } else {
        // Create
        res = await fetch(`${BACKEND_API}/api/contacts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save contact');
      }
    } catch (err) {
      alert('Error saving contact');
    }
    setLoading(false);
  };

  return (
    <div className="contact-modal-overlay">
      <div className="contact-modal-content">
        <h2>{contactToEdit ? 'Edit Contact' : 'Add Contact'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>First Name</label>
            <input
              type="text"
              value={form.first_name}
              onChange={e => setForm({ ...form, first_name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Last Name</label>
            <input
              type="text"
              value={form.last_name}
              onChange={e => setForm({ ...form, last_name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input
              type="text"
              value={form.phone_number}
              onChange={e => setForm({ ...form, phone_number: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Company Name</label>
            <input
              type="text"
              value={form.company_name}
              onChange={e => setForm({ ...form, company_name: e.target.value })}
              required
            />
          </div>
          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
            <button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Save'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContactModal;
