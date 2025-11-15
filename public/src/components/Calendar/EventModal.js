import React, { useState } from 'react';

const BACKEND_API = 'http://localhost:5000';

const EventModal = ({ isOpen, onClose, eventToEdit, slotInfo, onSave }) => {
  const [form, setForm] = useState({
    title: '',
    start: slotInfo ? slotInfo.start : '',
    end: slotInfo ? slotInfo.end : '',
  });
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (eventToEdit) {
      setForm({
        title: eventToEdit.title || '',
        start: eventToEdit.start,
        end: eventToEdit.end,
      });
    } else if (slotInfo) {
      setForm({ title: '', start: slotInfo.start, end: slotInfo.end });
    } else {
      setForm({ title: '', start: '', end: '' });
    }
  }, [eventToEdit, slotInfo, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (eventToEdit) {
        res = await fetch(`${BACKEND_API}/api/calendar-events/${eventToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      } else {
        res = await fetch(`${BACKEND_API}/api/calendar-events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save event');
      }
    } catch (err) {
      alert('Error saving event');
    }
    setLoading(false);
  };

  const handleDelete = async () => {
    if (!eventToEdit) return;
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_API}/api/calendar-events/${eventToEdit.id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to delete event');
      }
    } catch (err) {
      alert('Error deleting event');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{eventToEdit ? 'Edit Event' : 'Add Event'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title</label>
            <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Start</label>
            <input type="datetime-local" value={form.start} onChange={e => setForm({ ...form, start: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>End</label>
            <input type="datetime-local" value={form.end} onChange={e => setForm({ ...form, end: e.target.value })} required />
          </div>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>{eventToEdit ? 'Update' : 'Add'} Event</button>
            {eventToEdit && <button type="button" onClick={handleDelete} disabled={loading}>Delete</button>}
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EventModal;
