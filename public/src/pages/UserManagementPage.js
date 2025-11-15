import React, { useState, useEffect } from 'react';
import UserModal from '../components/UserManagement/UserModal';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userToEdit, setUserToEdit] = useState(null);

  const fetchUsers = () => {
    fetch(`${BACKEND_API}/api/users`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setUsers(data.items);
        else setUsers([]);
      })
      .catch(err => console.error('Failed to fetch users:', err));
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDisable = async (user) => {
    const res = await fetch(`${BACKEND_API}/api/users/${user.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isActive: !user.isActive }),
    });
    if (res.ok) {
      fetchUsers();
    } else {
      alert('Failed to update user status');
    }
  };

  return (
    <div className="user-management-page">
      <h1 className="page-title">User Management</h1>
      <button
        className="add-user-btn"
        onClick={() => {
          setIsModalOpen(true);
          setUserToEdit(null);
        }}
        style={{ marginBottom: '1rem' }}
      >
        Add User
      </button>
      <table className="users-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr><td colSpan={5}>No users found.</td></tr>
          ) : (
            users.map(user => (
              <tr key={user.id} style={!user.isActive ? { color: '#888', textDecoration: 'line-through' } : {}}>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.isActive ? 'Active' : 'Disabled'}</td>
                <td>
                  <button onClick={() => { setUserToEdit(user); setIsModalOpen(true); }}>Edit</button>
                  <button onClick={() => handleDisable(user)}>{user.isActive ? 'Disable' : 'Enable'}</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      <UserModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        userToEdit={userToEdit}
        onSave={fetchUsers}
      />
    </div>
  );
};

export default UserManagementPage;