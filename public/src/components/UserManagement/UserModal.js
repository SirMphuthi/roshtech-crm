import React, { useState } from 'react';

const BACKEND_API = 'http://localhost:5000';
const roles = ['Admin', 'User'];

const UserModal = ({ isOpen, onClose, userToEdit, onSave }) => {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'User',
  });
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (userToEdit) {
      setForm({
        full_name: userToEdit.full_name || '',
        email: userToEdit.email || '',
        password: '',
        role: userToEdit.role || 'User',
      });
    } else {
      setForm({ full_name: '', email: '', password: '', role: 'User' });
    }
  }, [userToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (userToEdit) {
        const { password, ...updateData } = form;
        res = await fetch(`${BACKEND_API}/api/users/${userToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateData),
        });
      } else {
        res = await fetch(`${BACKEND_API}/api/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save user');
      }
    } catch (err) {
      alert('Error saving user');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{userToEdit ? 'Edit User' : 'Add User'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
          </div>
          {!userToEdit && (
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
            </div>
          )}
          <div className="form-group">
            <label>Role</label>
            <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} required>
              {roles.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>{userToEdit ? 'Update' : 'Add'} User</button>
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserModal;
