import React, { useState } from 'react';

const BACKEND_API = 'http://localhost:5000';
const priorities = ['High', 'Medium', 'Low'];

const TaskModal = ({ isOpen, onClose, taskToEdit, onSave }) => {
  const [form, setForm] = useState({
    name: '',
    due_date: '',
    priority: 'Medium',
    related_to: '',
    status: 'Pending',
  });
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (taskToEdit) {
      setForm({
        name: taskToEdit.name || '',
        due_date: taskToEdit.due_date || '',
        priority: taskToEdit.priority || 'Medium',
        related_to: taskToEdit.related_to || '',
        status: taskToEdit.status || 'Pending',
      });
    } else {
      setForm({ name: '', due_date: '', priority: 'Medium', related_to: '', status: 'Pending' });
    }
  }, [taskToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (taskToEdit) {
        res = await fetch(`${BACKEND_API}/api/tasks/${taskToEdit.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      } else {
        res = await fetch(`${BACKEND_API}/api/tasks`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form),
        });
      }
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert('Failed to save task');
      }
    } catch (err) {
      alert('Error saving task');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{taskToEdit ? 'Edit Task' : 'Add Task'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Task Name</label>
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Due Date</label>
            <input type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Priority</label>
            <select value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} required>
              {priorities.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Related To</label>
            <input type="text" value={form.related_to} onChange={e => setForm({ ...form, related_to: e.target.value })} />
          </div>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>{taskToEdit ? 'Update' : 'Add'} Task</button>
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskModal;
