import React, { useState, useEffect } from 'react';
import { FiUserPlus, FiEdit, FiTrash2 } from 'react-icons/fi';
import ContactModal from '../components/Contacts/ContactModal';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000'; // Change to your backend endpoint if needed

const ContactsPage = () => {
  const [contacts, setContacts] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [contactToEdit, setContactToEdit] = useState(null);

  const fetchContacts = () => {
    fetch(`${BACKEND_API}/api/contacts`)
      .then((res) => res.json())
      .then((data) => {
        if (data.items) setContacts(data.items);
        else setContacts([]);
      })
      .catch((err) => console.error('Failed to fetch contacts:', err));
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  const handleDelete = async (contactId) => {
    const res = await fetch(`${BACKEND_API}/api/contacts/${contactId}`, { method: 'DELETE' });
    if (res.ok) {
      fetchContacts();
    } else {
      alert('Failed to delete contact');
    }
  };

  return (
    <div className="contacts-page">
      <h1 className="page-title">Contacts</h1>
      <button
        className="add-contact-btn"
        onClick={() => {
          setIsModalOpen(true);
          setContactToEdit(null);
        }}
        style={{ marginBottom: '1rem' }}
      >
        <FiUserPlus style={{ marginRight: 8 }} /> Add Contact
      </button>
      <table className="contacts-table">
        <thead>
          <tr>
            <th>Full Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Company Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {contacts.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center' }}>No contacts found.</td>
            </tr>
          ) : (
            contacts.map((contact) => (
              <tr key={contact.id}>
                <td>{contact.first_name} {contact.last_name}</td>
                <td>{contact.email}</td>
                <td>{contact.phone_number}</td>
                <td>{contact.account_name}</td>
                <td>
                  <button
                    className="edit-btn"
                    onClick={() => {
                      setIsModalOpen(true);
                      setContactToEdit(contact);
                    }}
                    title="Edit"
                  >
                    <FiEdit />
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(contact.id)}
                    title="Delete"
                    style={{ marginLeft: 8 }}
                  >
                    <FiTrash2 />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      <ContactModal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); setContactToEdit(null); }}
        contactToEdit={contactToEdit}
        onSave={fetchContacts}
      />
    </div>
  );
};

export default ContactsPage;